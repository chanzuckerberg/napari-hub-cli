from functools import lru_cache
from ..fs import ConfigFile, RepositoryFile
from iguala import as_matcher as m, regex as re


class GhActionWorkflowFolder(RepositoryFile):
    def __init__(self, path):
        super().__init__(path)
        workflows = []
        for gh_workflow_file in self.file.glob('**/*.yml'):
            workflows.append(GhActionWorkflow(gh_workflow_file))
        self.workflows = workflows


class GhActionWorkflow(ConfigFile):

    @lru_cache()
    def _extract_test_infos(self):
        pattern = m({
            'jobs>test': {
                'strategy>matrix': {
                    # 'platform': m([..., '@_', ...]) @ 'platforms',
                    'python-version': m([..., '@_', ...]) @ 'python_versions'
                },
                'steps': {
                    'run': re('^tox.*') | re('^python -m pytest .*') | re('^pytest.*')
                }
            }
        })

        result = pattern.match(self.data)
        if result.is_match:
            # platforms = result.bindings[0].get('platforms')
            py_versions = result.bindings[0].get('python_versions')
            py_versions = [tuple(int(x) for x in str(version).split('.')) for version in py_versions]
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
        pattern = m({
            'jobs>*>steps': {
                'uses': re('^codecov/.*')
            }
        })
        return pattern.match(self.data).is_match

