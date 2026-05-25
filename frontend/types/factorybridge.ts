export type UserRole = 'ADMIN' | 'OPERATOR' | 'CUSTOMER' | 'SUPPLIER';
export type RFQStatus = 'DRAFT' | 'SUBMITTED' | 'AI_REVIEWED' | 'QUOTING' | 'QUOTES_RECEIVED' | 'CUSTOMER_REVIEW' | 'CLOSED' | 'REJECTED';
export type RFQType = 'BY_DRAWING' | 'BY_3D_MODEL' | 'BY_PHOTO' | 'BY_SAMPLE' | 'TENDER_RFQ' | 'REGULAR_SUPPLY' | 'IMPORTED_PART_ALTERNATIVE';
export interface RFQSummary { id: string; number: string; title: string; category: string; quantity: string; status: RFQStatus | string; quotes: number; }
