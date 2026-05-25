export const adminMetrics = [
  { label: 'New RFQs', value: '12', note: '4 require operator review' },
  { label: 'Supplier Quotes', value: '28', note: '9 pending review' },
  { label: 'Active Orders', value: '7', note: '2 in sample production' },
  { label: 'High Risk Items', value: '3', note: 'compliance queue' },
];

export const adminRfqs = [
  { id: 'rfq-001', number: 'FB-RFQ-2026-000001', customer: 'Volga Industrial Parts', title: 'Aluminum CNC bracket by drawing', category: 'CNC_PARTS', aiScore: 82, status: 'AI_REVIEWED', operator: 'Fast Wind RFQ Desk' },
  { id: 'rfq-002', number: 'FB-RFQ-2026-000002', customer: 'North Repair Service', title: 'Rubber sealing ring by sample', category: 'RUBBER_PARTS', aiScore: 64, status: 'NEEDS_CLARIFICATION', operator: 'Unassigned' },
  { id: 'rfq-003', number: 'FB-RFQ-2026-000003', customer: 'TenderFulfill Pilot', title: 'Cast iron pump housing', category: 'CAST_PARTS', aiScore: 76, status: 'UNDER_OPERATOR_REVIEW', operator: 'Fast Wind RFQ Desk' },
];

export const adminSuppliers = [
  { id: 'sup-001', name: 'Ningbo Precision CNC', process: 'CNC_MACHINING', city: 'Ningbo', verification: 'DOCUMENT_VERIFIED', rating: '4.7', response: '8h' },
  { id: 'sup-002', name: 'Suzhou Industrial Parts', process: 'METAL_CASTING', city: 'Suzhou', verification: 'BASIC_VERIFIED', rating: '4.3', response: '14h' },
  { id: 'sup-003', name: 'Qingdao Rubber Tech', process: 'RUBBER_MOLDING', city: 'Qingdao', verification: 'UNDER_REVIEW', rating: 'N/A', response: '22h' },
];

export const adminQuotes = [
  { quote: 'FB-QT-2026-000001', rfq: 'FB-RFQ-2026-000001', supplier: 'Ningbo Precision CNC', unit: '$12.40', moq: '300', lead: '25 days', risk: 'LOW', status: 'SUBMITTED' },
  { quote: 'FB-QT-2026-000002', rfq: 'FB-RFQ-2026-000001', supplier: 'Suzhou Industrial Parts', unit: '$11.80', moq: '500', lead: '35 days', risk: 'MEDIUM', status: 'UNDER_REVIEW' },
  { quote: 'FB-QT-2026-000003', rfq: 'FB-RFQ-2026-000002', supplier: 'Qingdao Rubber Tech', unit: '$1.08', moq: '2000', lead: '18 days', risk: 'LOW', status: 'SUBMITTED' },
];

export const tenderInvitations = [
  { rfq: 'FB-RFQ-2026-000001', supplier: 'Ningbo Precision CNC', access: 'NDA_REQUIRED', status: 'QUOTE_SUBMITTED', deadline: '2026-06-01' },
  { rfq: 'FB-RFQ-2026-000001', supplier: 'Hangzhou Machining Group', access: 'FULL_ACCESS', status: 'VIEWED', deadline: '2026-06-01' },
  { rfq: 'FB-RFQ-2026-000003', supplier: 'Suzhou Industrial Parts', access: 'PREVIEW', status: 'INVITED', deadline: '2026-06-05' },
];

export const auditRows = [
  { actor: 'operator@factorybridge.local', action: 'RFQ_STATUS_CHANGED', object: 'FB-RFQ-2026-000001', time: '2026-05-24 10:15' },
  { actor: 'supplier@ningbo.local', action: 'QUOTE_SUBMITTED', object: 'FB-QT-2026-000001', time: '2026-05-24 11:02' },
  { actor: 'operator@factorybridge.local', action: 'LANDED_COST_CREATED', object: 'FB-RFQ-2026-000001', time: '2026-05-24 12:40' },
];
