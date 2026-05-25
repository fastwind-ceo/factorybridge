export const supplierProfile = {
  company: 'Ningbo Precision CNC Co., Ltd.',
  chineseName: '宁波精密数控制造有限公司',
  city: 'Ningbo',
  province: 'Zhejiang',
  verification: 'DOCUMENT_VERIFIED',
  responseTime: '8h avg',
  exportMarkets: 'Russia, Kazakhstan, UAE',
};

export const supplierCapabilities = [
  { process: 'CNC_MACHINING', materials: 'Aluminum, carbon steel, stainless steel', moq: '50 pcs', lead: '7 / 25 days', tags: ['FAST_SAMPLE', 'HAS_QC_TEAM'] },
  { process: 'TOOLING_MOLD_MAKING', materials: 'Aluminum fixtures, machining jigs', moq: '1 set', lead: '15 / 35 days', tags: ['HAS_ENGINEERS'] },
  { process: 'SURFACE_TREATMENT', materials: 'Anodizing, zinc plating, black oxide', moq: 'By batch', lead: '3 / 10 days', tags: ['OUTSOURCED_OK'] },
];

export const invitedRfqs = [
  { id: 'rfq-001', number: 'FB-RFQ-2026-000001', title: 'Aluminum CNC bracket by drawing', process: 'CNC_MACHINING', qty: '500 pcs', deadline: '2026-06-01', access: 'NDA_REQUIRED', status: 'ACCEPTED' },
  { id: 'rfq-004', number: 'FB-RFQ-2026-000004', title: 'Stainless steel shaft prototype', process: 'CNC_MACHINING', qty: '20 pcs', deadline: '2026-06-05', access: 'PREVIEW', status: 'INVITED' },
  { id: 'rfq-005', number: 'FB-RFQ-2026-000005', title: 'Machined tooling fixture set', process: 'TOOLING_MOLD_MAKING', qty: '4 sets', deadline: '2026-06-08', access: 'FULL_ACCESS', status: 'VIEWED' },
];

export const supplierQuotes = [
  { rfq: 'FB-RFQ-2026-000001', title: 'Aluminum CNC bracket', unit: '$12.40', moq: '300', sample: '$80', lead: '7 / 25 days', status: 'SUBMITTED' },
  { rfq: 'FB-RFQ-2026-000004', title: 'Stainless steel shaft prototype', unit: 'Draft', moq: '20', sample: '-', lead: 'Pending', status: 'DRAFT' },
];
