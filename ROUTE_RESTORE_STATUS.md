# Route Restore Status

Verified against `http://127.0.0.1:5180` on 2026-07-10.

| Route | Should exist? | Currently works? | Feature shown | Action taken | Remaining issue |
| --- | --- | --- | --- | --- | --- |
| `/` | yes | yes, HTTP 200 | Two-portal landing | Kept clean | None |
| `/citizen` | yes | yes, HTTP 200 | Citizen Portal with main voice assistant | Restored visible voice section | Browser voice depends on local browser support |
| `/government` | yes | yes, HTTP 200 | Full Government Portal | Added all major feature cards/actions | None |
| `/demo` | yes | yes, HTTP 200 | Original DemoDashboard | Restored route | Secondary route only |
| `/services` | yes | yes, HTTP 200 | Public services | Preserved | Sandbox catalog |
| `/apply/income_certificate` | yes | yes, HTTP 200 | Apply flow | Preserved | Sandbox application |
| `/applications` | yes | yes, HTTP 200 | My Applications | Preserved | Demo data |
| `/track` | yes | yes, HTTP 200 | Track Application | Preserved | Demo data |
| `/verify-certificate` | yes | yes, HTTP 200 | Public certificate verification | Preserved | Sandbox certificate/signature |
| `/officer` | yes | yes, HTTP 200 | Officer Review | Linked from Government Portal | Demo auth/data |
| `/admin` | yes | yes, HTTP 200 | Admin dashboard/login | Preserved | Requires login |
| `/admin/compliance` | yes | yes, HTTP 200 | Compliance Drift | Linked from Government Portal | Requires login |
| `/admin/policy-updates` | yes | yes, HTTP 200 | Circular and policy updates | Linked from Government Portal | Requires login |
| `/admin/propagation` | yes | yes, HTTP 200 | Connected-system propagation | Linked from Government Portal | Requires login |
| `/admin/audit` | yes | yes, HTTP 200 | Audit Trail | Linked from Government Portal | Requires login |
| `/admin/readiness` | yes | yes, HTTP 200 | Readiness & Ops | Linked from Government Portal | Requires login |
| `/virtual-gov` | yes | yes, HTTP 200 | Virtual Government Sandbox | Linked from Government Portal | Sandbox only |
| `/virtual-gov/gazette` | yes | yes, HTTP 200 | Virtual Gazette route family | Linked as Virtual Gazette | Same sandbox component family |
| `/virtual-gov/scenario-runner` | yes | yes, HTTP 200 | Scenario Runner route family | Linked as Scenario Runner | Same sandbox component family |
| `/mock/meeseva` | yes | yes, HTTP 200 | Mock MeeSeva connected system | Linked from Government Portal | Mock only |
| `/mock/public-faq` | yes | yes, HTTP 200 | Mock public FAQ/form | Linked from Government Portal | Mock only |
