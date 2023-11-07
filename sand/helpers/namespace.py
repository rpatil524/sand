from __future__ import annotations

from typing import TYPE_CHECKING, Mapping, Union, cast

from dependency_injector.wiring import Provide
from drepr.models.sm import SemanticModel
from sm.misc.funcs import import_func
from sm.namespaces.namespace import KnowledgeGraphNamespace

from sand.config import AppConfig

if TYPE_CHECKING:
    from sand.models.entity import Entity
    from sand.models.ontology import OntClass, OntProperty


class NamespaceService:
    def __init__(
        self,
        appcfg: AppConfig = Provide["appcfg"],
        default_entities: Mapping[str, Entity] = Provide["default_entities"],
        default_classes: Mapping[str, OntClass] = Provide["default_classes"],
        default_properties: Mapping[str, OntProperty] = Provide["default_properties"],
    ):
        self.appcfg = appcfg
        self.kgns: KnowledgeGraphNamespace = import_func(appcfg.kgns)()

        self.kgns_prefixes = self.kgns.prefix2ns.copy()
        self.kgns_prefixes.update(SemanticModel.get_default_prefixes())

        self.default_entities = default_entities
        self.default_classes = default_classes
        self.default_properties = default_properties

        self.uri2resource = {}
        self.id2resource = {}

        for odict in [
            self.default_entities,
            self.default_classes,
            self.default_properties,
        ]:
            for obj in cast(
                Mapping[str, Union["Entity", "OntClass", "OntProperty"]], odict
            ).values():
                assert obj.uri not in self.uri2resource
                self.uri2resource[obj.uri] = obj
                self.id2resource[obj.id] = obj

    def uri_to_id(self, uri: str):
        """Convert an URI to the corresponding ID"""
        if uri in self.uri2resource:
            return self.uri2resource[uri].id
        return self.kgns.uri_to_id(uri)

    def id_to_uri(self, id: str):
        """Convert an ID to the corresponding URI"""
        if id in self.id2resource:
            return self.id2resource[id].uri
        return self.kgns.id_to_uri(id)
