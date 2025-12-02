# VM Hosting Service Level Agreement (SLA)

**Supplier**: SUP3  
**Customer**: NovaTech Systems AG  
**Service**: VMHost v3.2  
**Version**: 2023-09  
**Effective Date**: 2023-09-15  
**Governing Law**: Switzerland

## 1. Service Description

VMHost v3.2 provides persistent virtual machines with networking, monitoring and automated host recovery. Several machine profiles are available for memory-intensive workloads.

## 2. Availability and Uptime Commitment

The supplier guarantees **99.9 percent monthly uptime**. Downtime includes any period where a VM becomes unreachable due to infrastructure issues.

## 3. Response Times and Incident Handling

- SEV1 outages → **15 minute** response
- Other severities → 1–6 hours depending on scope

## 4. Maintenance Windows

Weekly patching occurs Sunday mornings with **72 hours notice**. Some hypervisor or kernel updates may require VM restarts.

## 5. Service Credits

- Below 99.9 percent → **10 percent credit**
- Below 99.0 percent → **25 percent credit**

## 6. Customer Responsibilities

Customers must maintain guest OS security patches, firewall rules and snapshot management.

## 7. Data Protection and Privacy

Data resides in Swiss data centers unless replication is enabled. Logs retained for 30 days.

## 8. Security and Compliance

Includes encrypted disks, hardened hypervisors and support for multi factor authentication. Compliance documentation for ISO and SOC standards can be requested.

## 9. Limitations of Liability

Liability is limited to fees paid in the last 12 months. Indirect damages are excluded.

## 10. Termination

A 30-day notice period applies. Customers must delete all VMs before termination.

## 11. Exclusions

Planned maintenance, customer OS faults, external network failures and unsupported features.

## 12. Region Specific Terms

Swiss regulations may require specific retention periods for audit logs in regulated industries.

## 13. Definitions

- **VM Availability**: VM is reachable and operational
- **Downtime**: Infrastructure-caused inaccessibility
- **Service Credit**: Credit applied to future invoices
