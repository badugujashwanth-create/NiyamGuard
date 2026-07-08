from app.models.cascade_models import CascadeTrace
from app.services.platform_store import add_audit_event, now_iso, read_store, write_store


TRACE_TEMPLATES = {
    "portal": [
        "Circular Changed",
        "Portal Not Updated",
        "Officer Uses Outdated Portal Validation",
        "Citizen Applies Under Wrong Rule",
        "Wrong Approval or Rejection Risk",
    ],
    "faq": [
        "Circular Changed",
        "Public FAQ Not Updated",
        "Citizen Reads Wrong Requirement",
        "Citizen Uploads Wrong Document",
        "Application Delay or Rejection Risk",
    ],
    "sop": [
        "Circular Changed",
        "SOP Manual Not Updated",
        "Officer Follows Old Instruction",
        "Wrong Manual Verification",
        "Citizen Harm Risk",
    ],
}


def generate_trace(finding_id: str) -> CascadeTrace | None:
    store = read_store()
    finding = next((item for item in store.compliance_findings if item.id == finding_id), None)
    if finding is None:
        return None
    system = next((item for item in store.connected_systems if item.id == finding.connected_system_id), None)
    if system is None:
        return None
    labels = TRACE_TEMPLATES.get(
        system.system_type,
        ["Circular Changed", "System Not Updated", "Citizen Receives Wrong Guidance", "Citizen Harm Risk"],
    )
    nodes = [{"id": f"node_{index + 1}", "label": label} for index, label in enumerate(labels)]
    edges = [
        {"from": nodes[index]["id"], "to": nodes[index + 1]["id"]}
        for index in range(len(nodes) - 1)
    ]
    trace = CascadeTrace(
        id=f"trace_{finding.id}",
        finding_id=finding.id,
        trace_type=system.system_type,
        nodes_json=nodes,
        edges_json=edges,
        impact_summary=f"{system.name}: {labels[-1]} because {finding.finding_summary}",
        created_at=now_iso(),
    )
    store.cascade_traces = [item for item in store.cascade_traces if item.finding_id != finding.id]
    store.cascade_traces.append(trace)
    add_audit_event(store, "cascade_trace_generated", {"finding_id": finding.id})
    write_store(store)
    return trace


def get_trace_for_finding(finding_id: str) -> CascadeTrace | None:
    store = read_store()
    trace = next((item for item in store.cascade_traces if item.finding_id == finding_id), None)
    return trace or generate_trace(finding_id)


def traces_by_service(service_id: str) -> list[CascadeTrace]:
    store = read_store()
    service_finding_ids = {
        finding.id for finding in store.compliance_findings if finding.service_id == service_id
    }
    traces = [trace for trace in store.cascade_traces if trace.finding_id in service_finding_ids]
    missing = service_finding_ids - {trace.finding_id for trace in traces}
    for finding_id in missing:
        generated = generate_trace(finding_id)
        if generated:
            traces.append(generated)
    return traces
