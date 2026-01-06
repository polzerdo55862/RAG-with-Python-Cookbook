# Cloud Compute Service Level Agreement (SLA)

**Supplier**: Alpha Cloud GmbH  
**Customer**: Smart Industries AG  
**Service**: Alpha Compute v1.4  
**Version**: 2024-01  
**Effective Date**: 2024-01-01  
**Governing Law**: Germany

## 1. Service Description

The Alpha Compute service provides virtual compute resources including CPU, memory and temporary storage. The service is accessible through the Alpha Cloud Management Console and the public API.
Customers may provision compute instances, manage workloads and monitor utilisation metrics. The service is available in the EU-Central, EU-West and US-East regions.
Instance performance may vary depending on workload patterns and CPU family. Temporary storage is not replicated and should not be used for persistent data.

## 2. Availability and Uptime Commitment

Alpha Cloud commits to a **monthly uptime percentage of 99.9 percent** for all running compute instances.
Uptime is measured per region based on the ability of the service control plane to create, start or manage compute instances.
Downtime refers to any period of five or more consecutive minutes during which the customer is unable to perform instance operations due to a service-side failure.
This commitment does not apply to scheduled maintenance, customer induced faults or events described in the “Exclusions” section.

## 3. Response Times and Incident Handling

Alpha Cloud provides 24x7 incident handling for critical issues affecting production workloads.
Incidents are classified into four severity levels ranging from SEV1 to SEV4.
For SEV1 (critical production outage), Alpha Cloud commits to an **initial response time of 15 minutes** and continuous work until the issue is resolved or a workaround is available.
For non critical incidents, response times vary from 1 to 12 hours depending on severity.
The customer must provide complete diagnostic information to allow effective troubleshooting.

## 4. Maintenance Windows

Alpha Cloud may perform routine maintenance to maintain the stability and security of the compute infrastructure.
Scheduled maintenance will be announced at least **72 hours in advance** and typically occurs on Sundays between 01:00 and 05:00 CET.
During scheduled maintenance, brief periods of reduced control plane availability may occur, but compute instances are expected to continue running.
Emergency maintenance may be performed without prior notice if required to address an immediate security threat or service stability risk.

## 5. Service Credits

If the monthly uptime percentage falls below the committed level of 99.9 percent, the customer becomes eligible for service credits.
The credit amount is based on the severity of the SLA violation.
A monthly uptime of 99.0 to 99.9 percent results in a 10 percent credit on the monthly service bill.
Below 99.0 percent uptime, the credit increases to 25 percent.
Service credits are applied to future invoices and cannot be redeemed for cash.

## 6. Customer Responsibilities

The customer is responsible for configuring compute instances, managing access control and ensuring secure operation of their workloads.
The customer must maintain up to date operating system patches and follow Alpha Cloud security recommendations.
Misconfigurations, application bugs or insufficient resource allocation are not considered SLA violations.
The customer must ensure backups are stored outside the compute instance to avoid data loss.

## 7. Data Protection and Privacy

Alpha Cloud processes customer data in accordance with GDPR and internal data protection standards.
No customer data is transferred outside of the selected region unless explicitly configured by the customer.
Diagnostic logs collected during incident handling may include resource identifiers but exclude personal data unless provided by the customer.
Data retention for logs is 30 days unless longer retention is required for security investigations.

## 8. Security and Compliance

Alpha Cloud implements standard security controls including encryption in transit, access logging, multi factor authentication support and regular penetration testing.
Customers may request audit reports including SOC 2 Type II and ISO 27001 certificates.
Security vulnerabilities reported by customers will be triaged within 48 hours.
Alpha Cloud may disable compute instances that present a critical threat to platform stability.

## 9. Limitations of Liability

Alpha Cloud’s total aggregate liability under this SLA is limited to the amount paid by the customer for the compute service in the previous twelve months.
Alpha Cloud is not liable for indirect, incidental or consequential damages including lost profits, data loss or service interruption caused by customer applications.
Nothing in this SLA limits liability in cases of gross negligence or intentional misconduct.

## 10. Termination

The SLA may be terminated by either party with 30 days written notice.
If the customer terminates the SLA before the end of the billing period, no partial refunds are provided.
Upon termination, all compute instances must be shut down and deleted by the customer, and all associated data must be removed from the service.

## 11. Exclusions

This SLA does not apply to:

- planned maintenance windows,
- failures caused by customer applications or misconfigurations,
- network issues outside Alpha Cloud’s control,
- distributed denial of service attacks,
- beta or experimental features,
- any service used in violation of the Acceptable Use Policy.

## 12. Region Specific Terms

In the EU-Central region, maintenance windows may include network rebalancing.
In the US-East region, redundancy is reduced during hurricane season.
Local compliance rules may require additional logging or retention for specific industries.
Customers operating in regulated sectors must request region specific compliance documentation.

## 13. Definitions

- **Uptime**: The portion of time during which compute instance operations succeed within a region.
- **Downtime**: A period of at least five consecutive minutes during which the service control plane is not functioning.
- **SEV1 Incident**: A critical production issue where no workaround exists.
- **Service Credit**: A financial credit applied to future invoices due to SLA violation.
