from dataclasses import asdict
from functools import partial
from typing import Callable, Dict, List, Optional

from playhouse.shortcuts import model_to_dict

import sm.outputs as O
from smc.models import SemanticModel, Table
from smc.models.entity import Entity, EntityAR
from smc.models.ontology import OntProperty, OntClass, OntPropertyAR, OntClassAR


def serialize_entity(ent: Entity):
    return {
        "id": ent.id,
        "label": ent.label,
        "aliases": ent.aliases,
        "description": ent.description,
        "properties": {
            prop: [
                {
                    "value": asdict(stmt.value),
                    "qualifiers": {
                        qid: [asdict(qval) for qval in qvals]
                        for qid, qvals in stmt.qualifiers.items()
                    },
                    "qualifiers_order": stmt.qualifiers_order,
                }
                for stmt in stmts
            ]
            for prop, stmts in ent.properties.items()
        },
    }


def serialize_graph(
    sm: O.SemanticModel,
    uri2label: Callable[[str, bool], Optional[str]],
    columns: List[str],
):
    nodes = []
    for n in sm.iter_nodes():
        if isinstance(n, O.ClassNode):
            nodes.append(
                {
                    "id": n.id,
                    "uri": n.abs_uri,
                    "label": uri2label(n.abs_uri, True) or n.rel_uri,
                    "approximation": n.approximation,
                    "type": "class_node",
                }
            )
        elif isinstance(n, O.DataNode):
            nodes.append(
                {
                    "id": n.id,
                    "label": columns[n.col_index],
                    "type": "data_node",
                    "column_index": n.col_index,
                }
            )
        else:
            if n.datatype == O.LiteralNodeDataType.Entity:
                value = Entity.uri2id(n.value)
            else:
                value = n.value
            nodes.append(
                {
                    "id": n.id,
                    "value": value,
                    "label": n.label,
                    "type": "literal_node",
                    "is_in_context": n.is_in_context,
                    "datatype": n.datatype.value,
                }
            )

    edges = [
        {
            "source": e.source,
            "target": e.target,
            "uri": e.abs_uri,
            "label": uri2label(e.abs_uri, False) or e.rel_uri,
            "approximation": e.approximation,
        }
        for e in sm.iter_edges()
    ]

    return dict(nodes=nodes, edges=edges)


def serialize_sm(sm: SemanticModel):
    ontprops = OntPropertyAR()
    ontclasses = OntClassAR()

    uri2lbl = partial(get_label, ontprops=ontprops, ontclasses=ontclasses)
    output = model_to_dict(sm, recurse=False)
    output["data"] = serialize_graph(output["data"], uri2lbl, sm.table.columns)
    return output


def batch_serialize_sms(sms: List[SemanticModel]):
    tbls = {sm.table_id for sm in sms}  # type: ignore
    tbls = {
        tbl.id: tbl
        for tbl in Table.select(Table.id, Table.columns).where(Table.id.in_(tbls))  # type: ignore
    }

    ontprops = OntPropertyAR()
    ontclasses = OntClassAR()

    uri2lbl = partial(get_label, ontprops=ontprops, ontclasses=ontclasses)

    output = []
    for sm in sms:
        r = model_to_dict(sm, recurse=False)
        r["data"] = serialize_graph(r["data"], uri2lbl, tbls[sm.table_id].columns)  # type: ignore
        output.append(r)
    return output


def get_label(
    id: str,
    is_class: bool,
    ontprops: Dict[str, OntProperty],
    ontclasses: Dict[str, OntClass],
) -> Optional[str]:
    if is_class:
        if id in ontclasses:
            return ontclasses[id].readable_label
        elif id in ontprops:
            return ontprops[id].readable_label
    else:
        if id in ontprops:
            return ontprops[id].readable_label
        elif id in ontclasses:
            return ontclasses[id].readable_label
    return None
