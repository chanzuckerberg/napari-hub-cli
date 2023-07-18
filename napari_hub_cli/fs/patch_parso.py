from parso.python import tree as cst


def get_body_node(self):
    if self.type in ("simple_stmt", "decorated"):
        return [c for c in self.children if c.type != 'newline']
    if self.type == "atom_expr":
        return self.children[:-1]
    if self.type == "suite":
        body = []
        for x in self.children:
            if not isinstance(x, cst.PythonNode) and x.type not in ("newline", "keyword"):
                body.append(x)
            else:
                body.extend(get_body_node(x))
        return body
    return []

setattr(cst.PythonNode, "body", property(get_body_node))


def get_body_children(self):
    body = []
    for x in self.children:
        if x.type in ("newline", "keyword"):
            continue
        if x.type in ("simple_stmt", "suite"):
            body.extend(x.body)
        else:
            body.append(x)
    return body


setattr(cst.PythonBaseNode, "content", property(lambda self: self.children))
setattr(cst.Module, "body", property(get_body_children))
setattr(cst.ClassOrFunc, "body", property(get_body_children))
setattr(cst.ClassOrFunc, "decorator_names", property(lambda self: [d.children[1].get_code().strip() for d in self.get_decorators()]))
setattr(cst.ClassOrFunc, "decorators", property(lambda self: [d.children[1] for d in self.get_decorators()]))
setattr(cst.Import, 'names', property(lambda self: self.get_paths()[0]))
setattr(cst.Import, 'alias', property(lambda self: ".".join(n.value for n in self.get_defined_names())))
setattr(cst.ImportFrom, 'module', property(lambda self: ".".join(n.value for n in self.get_from_names())))
setattr(cst.PythonBaseNode, 'lineno', property(lambda self: self.start_pos[0]))