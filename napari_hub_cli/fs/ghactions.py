from operator import is_not
import re
from functools import lru_cache
from pathlib import Path

import requests
from iguala import as_matcher as m
from iguala import regex
from iguala import is_not

from ..utils import build_gh_header, extract_if_match

from ..fs import ConfigFile, RepositoryFile


class GhActionWorkflow(ConfigFile):
    @lru_cache()
    def _extract_test_infos(self):
        pattern = m(
            {
                "jobs>*": m(
                    {
                        "strategy>matrix": m(
                            {"python": m([..., "@_", ...]) @ "python_versions"}
                        )
                        | {"python-version": m([..., "@_", ...]) @ "python_versions"},
                        "steps>*": m(
                            {
                                "run": regex("tox")
                                | regex("python -m tox")
                                | regex("python -m pytest")
                                | regex("pytest")
                                | regex(".*unittest.*")
                            }
                        )
                        | {"uses": regex(".*test.*")},
                    }
                )
            }
        )

        result = pattern.match(self.data)
        if result.is_match:
            py_versions = result.bindings[0].get("python_versions")
            py_versions = [
                tuple(int(x) for x in str(version).split(".") if x)
                for version in py_versions
            ]
            return py_versions

        pattern = m(
            {
                "jobs>*": {
                    "steps>*": {
                        "run": regex("tox")
                        | regex("python -m tox")
                        | regex("python -m pytest")
                        | regex("pytest")
                        | regex(".*unittest.*")
                    },
                    "steps>*>python-version": m([..., "@_", ...]) @ "python_versions"
                    | "@python_versions",
                }
            }
        )

        result = pattern.match(self.data)
        if result.is_match:
            for binding in result.bindings:
                py_versions = binding.get("python_versions")
                if str(py_versions).startswith("$"):
                    continue
                if not isinstance(py_versions, list):
                    py_versions = [py_versions]
                py_versions = [
                    tuple(int(x) for x in str(version).split(".") if x)
                    for version in py_versions
                ]
                return py_versions

        return None

    @property
    def defines_test(self):
        res = self._extract_test_infos()
        return res is not None

    @property
    def supported_python_version(self):
        res = self._extract_test_infos()
        return res if res else []

    @property
    def defines_codecov_coverage(self):
        pattern = m({"jobs>*>steps": {"uses": regex("^codecov/.*")}})
        return pattern.match(self.data).is_match


class GhActionWorkflowFolder(RepositoryFile):
    GITHUB_PATTERN = r"https://github.com/(?P<owner>[^/]+)/(?P<repo>.+)"
    CODECOV_API = "https://api.codecov.io/graphql/gh"
    CODECOV_QUERY_OLD = """
query GetRepoCoverage($name: String!, $repo: String!, $branch: String!){
    owner(username:$name){
        repository(name:$repo){
            branch(name:$branch){
                name
                head {
                    totals {
                        percentCovered
                        lineCount
                        hitsCount
                    }
                }
            }
        }
    }
}
"""
    CODECOV_QUERY = """
query GetRepoCoverage($name: String!, $repo: String!, $branch: String!) {
      owner(username:$name){
        repository: repositoryDeprecated(name:$repo){
          branch(name:$branch) {
            name
            head {
              yamlState
              totals {
                percentCovered
                lineCount
                hitsCount
              }
            }
          }
        }
      }
    }
"""

    def __init__(self, path, url):
        super().__init__(path)
        self.url = url
        if url and url.endswith(".git"):
            self.url = url[:-4]
        workflows = []
        for gh_workflow_file in self.file.glob("**/*.yml"):
            workflows.append(GhActionWorkflow(gh_workflow_file))
        self.workflows = workflows

    @property
    def gh_test_config(self):
        return next((f for f in self.workflows if f.defines_test), None)

    @property
    def gh_codecov_config(self):
        return next((f for f in self.workflows if f.defines_codecov_coverage), None)

    def _compute_call_url(self):
        if not re.match(self.GITHUB_PATTERN, self.url):
            return None
        api_url = self.url.replace(
            "https://github.com/", "https://api.github.com/repos/"
        )
        return api_url

    @lru_cache()
    def _identify_EOI(self, config):
        """Gets the Entry Of Interest that own information about the workflow execution."""
        api_url = self._compute_call_url()
        if not api_url:
            return None
        try:
            response = requests.get(f"{api_url}/actions/runs", headers=build_gh_header())
            if response.status_code != requests.codes.ok:
                response.raise_for_status()  # pragma: no cover
            response_json = response.json()
            entry = next(
                x
                for x in response_json["workflow_runs"]
                if config
                and str(Path(x.get("path", "__nothing__"))) in str(config.file)
                and x.get("head_branch") in ("main", "master")
                and x.get("status") == "completed"
            )
            return entry
        except StopIteration:
            return None
        except Exception as e:  # pragma: no cover
            raise e

    def _pull_jobs_details(self, eoi):
        if not eoi:
            return {}
        response = requests.get(eoi["jobs_url"], headers=build_gh_header())
        if response.status_code != requests.codes.ok:
            return {}  # pragma: no cover
        return response.json()

    @property
    def has_successful_tests(self):
        eoi = self._identify_EOI(self.gh_test_config)
        return eoi is not None and eoi["conclusion"] == "success"


    @property
    def details_failing_tests(self):
        pattern = m(
            {
                "jobs": {
                    "name": "@job_name",
                    "conclusion": is_not("success"),   # type: ignore
                    "labels": "@platform",
                    "steps": {
                        "name": "@step_name",
                        "conclusion": "cancelled",
                        "status": "completed"
                    }
                }
            }
        )

        jobs = self._pull_jobs_details(self._identify_EOI(self.gh_test_config))
        result = pattern.match(jobs)
        if not result.is_match:
            return "None"
        infos = extract_if_match(
            result, lambda b: (b["platform"], b["job_name"], b["step_name"])
        )
        infos_dict = {}
        for platform, *r in infos:
            infos_dict.setdefault(platform, []).append(r)
        res_string = ""
        for platform, step_infos in infos_dict.items():
            res_string += f"\n[red]   {platform}[/red]"
            for job_name, step_name in step_infos:
                res_string += f"\n     - [ {job_name} ] {step_name}"
        return res_string

    def query_codecov_result(self):
        coi = self._identify_EOI(self.gh_codecov_config)
        if not coi:
            return None
        api_url = self._compute_call_url()
        try:
            response = requests.get(f"{api_url}/commits/{coi['head_sha']}/status", headers=build_gh_header())
            if response.status_code != requests.codes.ok:
                response.raise_for_status()  # pragma: no cover
            response_json = response.json()
            entry = next(
                (
                    x
                    for x in response_json["statuses"]
                    if x["context"].startswith("codecov")
                )
            )
            m = re.match(r"^(\d+(\.\d+)*)%.*", entry["description"])
            if m:
                return float(m.group(1))
            return None
        except StopIteration:
            return None
        except Exception as e:  # pragma: no cover
            raise e

    @lru_cache()
    def query_codecov_api(self):
        match_result = re.match(self.GITHUB_PATTERN, self.url)
        if not match_result:
            return None
        owner, repo = match_result.groupdict().values()
        json_payload = {
            "query": self.CODECOV_QUERY,
            "variables": {"name": owner, "repo": repo, "branch": "main"},
        }
        response = requests.post(self.CODECOV_API, json=json_payload)
        json_r = response.json()
        try:
            if json_r["data"]["owner"]["repository"]["branch"] is None:
                json_payload["variables"]["branch"] = "master"
                response = requests.post(self.CODECOV_API, json=json_payload)
                json_r = response.json()
                if json_r["data"]["owner"]["repository"]["branch"] is None:
                    return None
            return json_r["data"]["owner"]["repository"]["branch"]["head"]["totals"][
                "percentCovered"
            ]
        except Exception:
            return None

    @property
    def reported_codecov_result(self):
        return self.query_codecov_api()

    @property
    def has_codecove_results(self):
        return self.query_codecov_api() is not None

    @property
    def has_codecove_more_80(self):
        result = self.query_codecov_api()
        return result is not None and result >= 80  # type: ignore
