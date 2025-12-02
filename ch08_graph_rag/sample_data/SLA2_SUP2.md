# Cloud Storage Service Level Agreement (SLA)

**Supplier**: SUP2  
**Customer**: Example Customer AG  
**Service**: Storage v2.0  
**Version**: 2023-07  
**Effective Date**: 2023-07-01  
**Governing Law**: Netherlands

## 1. Service Description

Storage v2.0 provides redundant object and block storage with multiple access tiers. Customers can perform read, write and management operations through console, CLI or API.

## 2. Availability and Uptime Commitment

The supplier guarantees **99.95 percent monthly availability** for storage operations. Downtime includes periods where the API is unable to complete read or write requests.

## 3. Response Times and Incident Handling

- SEV1 outages → **15 minute** response
- SEV2–SEV3 → 1–8 hour response based on business impact

## 4. Maintenance Windows

Scheduled maintenance is announced **48 hours in advance**. Minor latency spikes may occur, though data remains available. Emergency security patches may be applied immediately.

## 5. Service Credits

- 99.0–99.95 percent → **10 percent credit**
- Below 99.0 percent → **25 percent credit**

## 6. Customer Responsibilities

Customers must configure IAM correctly, manage backup policies and apply appropriate data lifecycle rules.

## 7. Data Protection and Privacy

Data stored in the Netherlands remains within EU jurisdiction except when cross-region replication is enabled.

## 8. Security and Compliance

Storage is encrypted at rest and in transit. Security programs include vulnerability scanning and compliance certifications (ISO, SOC, GDPR).

## 9. Limitations of Liability

Liability is capped at the previous twelve months of storage charges. Customer misconfigurations are excluded.

## 10. Termination

Customers must export and remove data when terminating the SLA.

## 11. Exclusions

Planned maintenance, customer misuse, unsupported beta features and customer-induced security breaches.

## 12. Region Specific Terms

Data residency rules may require enhanced audit logging for certain industries.

## 13. Definitions

- **Durability**: Likelihood that data remains intact over one year
- **Availability**: Ability to perform storage operations
- **Service Credit**: Invoice credit based on SLA violation
