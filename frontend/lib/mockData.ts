export const mockRfqs = [
  { id: 'rfq-001', number: 'FB-RFQ-2026-000001', title: 'Aluminum CNC bracket by drawing', category: 'CNC_PARTS', quantity: '500 pcs', status: 'AI_REVIEWED', quotes: 3 },
  { id: 'rfq-002', number: 'FB-RFQ-2026-000002', title: 'Rubber sealing ring by sample', category: 'RUBBER_PARTS', quantity: '2,000 pcs', status: 'QUOTING', quotes: 1 },
  { id: 'rfq-003', number: 'FB-RFQ-2026-000003', title: 'Cast iron pump housing', category: 'CAST_PARTS', quantity: '80 pcs', status: 'SUBMITTED', quotes: 0 },
];

export const quoteRows = [
  { supplier: 'Ningbo Precision CNC', unit: '$12.40', moq: '300', tooling: '$0', lead: '25 days', landed: '$19.10', risk: 'LOW' },
  { supplier: 'Suzhou Industrial Parts', unit: '$11.80', moq: '500', tooling: '$0', lead: '35 days', landed: '$18.90', risk: 'MEDIUM' },
  { supplier: 'Hangzhou Machining Group', unit: '$13.20', moq: '200', tooling: '$0', lead: '18 days', landed: '$20.40', risk: 'LOW' },
];

export const notifications = [
  { id: 'n1', title: 'Quote received', body: 'Ningbo Precision CNC submitted a quote for FB-RFQ-2026-000001.' },
  { id: 'n2', title: 'AI review completed', body: 'Completeness score: 82%. Missing field: surface finish.' },
  { id: 'n3', title: 'Landed cost ready', body: 'DDP Moscow estimate has been prepared by operator.' },
];
