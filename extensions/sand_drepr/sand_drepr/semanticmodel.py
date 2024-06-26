from typing import Callable, List, Mapping, Optional, Set

import drepr.models.sm as drepr_sm
import sm.outputs.semantic_model as O
from sm.misc.funcs import assert_not_null
from sm.namespaces.prelude import KnowledgeGraphNamespace

from sand.config import AppConfig
from sand.helpers.namespace import NamespaceService
from sand.models.ontology import OntProperty, OntPropertyDataType

# mapping from predefined datatypes to D-REPR datatype
datatype_mapping: Mapping[OntPropertyDataType, Optional[drepr_sm.DataType]] = {
    "globe-coordinate": drepr_sm.DataType(
        "http://www.opengis.net/ont/geosparql#wktLiteral",
        {"geo": "http://www.opengis.net/ont/geosparql#"},
    ),
    "url": drepr_sm.PredefinedDataType.xsd_anyURI.value,
    "entity": drepr_sm.PredefinedDataType.drepr_uri.value,
    "string": drepr_sm.PredefinedDataType.xsd_string.value,
    "integer-number": drepr_sm.PredefinedDataType.xsd_int.value,
    "decimal-number": drepr_sm.PredefinedDataType.xsd_decimal.value,
    "datetime": drepr_sm.PredefinedDataType.xsd_dateTime.value,
}


def get_drepr_sm(
    sm: O.SemanticModel,
    kgns: NamespaceService,
    kgns_prefixes: dict[str, str],
    ontprop_ar: Mapping[str, OntProperty],
    ident_props: set[str],
    get_attr_id: Callable[[int], str],
    get_ent_attr_id: Callable[[int], str],
) -> drepr_sm.SemanticModel:
    """Convert sm model into drepr model.

    Args:
        sm: the semantic model we want to convert
        kgns: the knowledge graph namespace
        kgns_prefixes: the prefixes of the knowledge graph namespace
        ontprop_ar: mapping from the id to ontology property
        ident_props: list of properties that telling a data node contains entities (e.g., rdfs:label)
        get_attr_id: get attribute id from column index
        get_ent_attr_id: for each entity column, to generate url, we create an extra attribute containing the entity uri, this function get its id based on the column index
    """
    nodes = {}
    edges = {}

    for node in sm.nodes():
        if isinstance(node, O.ClassNode):
            nodes[str(node.id)] = drepr_sm.ClassNode(
                node_id=str(node.id), label=node.rel_uri
            )
        elif isinstance(node, O.DataNode):
            # find data type of this node, when they have multiple data types
            # that do not agree with each other, we don't set the datatype
            # usually, that will be displayed from the UI so users know that

            datatypes: Set[OntPropertyDataType] = {
                assert_not_null(ontprop_ar[kgns.uri_to_id(inedge.abs_uri)]).datatype
                for inedge in sm.in_edges(node.id)
            }
            datatype = (
                datatype_mapping.get(list(datatypes)[0], None)
                if len(datatypes) == 1
                else None
            )

            nodes[str(node.id)] = drepr_sm.DataNode(
                node_id=str(node.id),
                attr_id=get_attr_id(node.col_index),
                data_type=datatype,
            )
        elif isinstance(node, O.LiteralNode):
            if node.datatype == O.LiteralNodeDataType.Entity:
                datatype = drepr_sm.PredefinedDataType.drepr_uri.value
            else:
                assert node.datatype == O.LiteralNodeDataType.String
                datatype = drepr_sm.PredefinedDataType.xsd_string.value

            nodes[str(node.id)] = drepr_sm.LiteralNode(
                node_id=str(node.id), value=node.value, data_type=datatype
            )

    used_ids = {x for edge in sm.edges() for x in [str(edge.source), str(edge.target)]}
    for node_id in set(nodes.keys()).difference(used_ids):
        del nodes[node_id]

    for edge in sm.edges():
        edges[len(edges)] = drepr_sm.Edge(
            edge_id=len(edges),
            source_id=str(edge.source),
            target_id=str(edge.target),
            label=edge.rel_uri,
        )

    # print(edges)

    # add drepr:uri relationship
    for node in get_entity_data_nodes(sm, ident_props):
        new_node_id = str(node.id) + ":ents"
        nodes[new_node_id] = drepr_sm.DataNode(
            node_id=new_node_id,
            attr_id=get_ent_attr_id(node.col_index),
            data_type=drepr_sm.PredefinedDataType.drepr_uri.value,
        )
        inedges = [
            inedge for inedge in sm.in_edges(node.id) if inedge.abs_uri in ident_props
        ]
        assert len(inedges) == 1
        inedge = inedges[0]
        edges[len(edges)] = drepr_sm.Edge(
            edge_id=len(edges),
            source_id=str(inedge.source),
            target_id=new_node_id,
            # special predicate telling drepr to use as uri of entity, instead of generating a blank node
            label="drepr:uri",
        )

    prefixes = kgns_prefixes.copy()
    prefixes.update(drepr_sm.SemanticModel.get_default_prefixes())
    return drepr_sm.SemanticModel(
        nodes=nodes,
        edges=edges,
        prefixes=prefixes,
    )


def get_entity_data_nodes(
    sm: O.SemanticModel, ident_props: set[str]
) -> List[O.DataNode]:
    ent_dnodes = []
    for node in sm.iter_nodes():
        if not isinstance(node, O.DataNode):
            continue

        stypes = sm.get_semantic_types_of_column(node.col_index)
        if any(stype.predicate_abs_uri in ident_props for stype in stypes):
            ent_dnodes.append(node)

    return ent_dnodes
