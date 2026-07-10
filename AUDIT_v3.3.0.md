# Bellwether v3.3.0 Evidence Ledger

## Pre-edit inspection
The v3.2.1 code already contained three player enterprises, owner/manager modes, wages, reputation, health, closure pressure, property/work-room gates, transport cargo, dynamic village outlook and input consumption. Those claims were therefore treated as existing systems, not reimplemented.

## Confirmed design gap
Owner-operated enterprise sessions consumed raw inputs and immediately created revenue in the same action. Manager-operated enterprises created daily income without consuming prepared stock. This bypassed a meaningful production/logistics chain and allowed staff to generate sales from no goods.

## v3.3.0 extension
- Enterprise schema migration adds prepared stock, stock capacity, batch history, deliveries and missed-sales counters.
- Owner operation is split into Prepare Stock and Open for Customers.
- Preparation consumes the existing authoritative input paths.
- Higher cargo-capacity transport can prepare larger batches, connecting transport progression to small-town logistics without creating a new vehicle truth system.
- Customer sessions consume stock and record units sold.
- Manager-operated businesses consume stock; empty stock produces missed sales rather than imaginary income.
- Life Book gains a Work surface showing enterprise health, reputation, stock, sales, cash and supply warnings.
- No village-business economy, property authority or transport authority was replaced.

## Verification boundary
Deterministic production-chain contracts are tested locally. Long-run balance and live Town Consciousness interference remain campaign-level evidence tasks and are not claimed from source inspection alone.
