export const workflowTemplates = [
  {
    id: 'simplified_credit',
    title: 'Simplified Credit Application',
    description: 'Alur kerja kredit sederhana: input data pemohon, data fasilitas, data keuangan, dan approval manager.',
    icon: 'LucideFileText',
    color: 'from-purple-500 to-violet-600',
    marketplaceCategory: 'Credit',
    xml: `<?xml version="1.0" encoding="UTF-8"?>
<bpmn:definitions xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"
                  xmlns:bpmn="http://www.omg.org/spec/BPMN/20100524/MODEL"
                  xmlns:bpmndi="http://www.omg.org/spec/BPMN/20100524/DI"
                  xmlns:dc="http://www.omg.org/spec/DD/20100524/DC"
                  xmlns:di="http://www.omg.org/spec/DD/20100524/DI"
                  id="Definitions_1"
                  targetNamespace="http://bpmn.io/schema/bpmn">
  <bpmn:process id="Process_1" isExecutable="true">
    <bpmn:startEvent id="StartEvent_1" name="Mulai">
      <bpmn:outgoing>Flow_1</bpmn:outgoing>
    </bpmn:startEvent>
    <bpmn:userTask id="FormBorrower" name="Data Pemohon">
      <bpmn:incoming>Flow_1</bpmn:incoming>
      <bpmn:outgoing>Flow_2</bpmn:outgoing>
    </bpmn:userTask>
    <bpmn:userTask id="FormFacility" name="Data Fasilitas">
      <bpmn:incoming>Flow_2</bpmn:incoming>
      <bpmn:outgoing>Flow_3</bpmn:outgoing>
    </bpmn:userTask>
    <bpmn:userTask id="FormFinancial" name="Data Keuangan">
      <bpmn:incoming>Flow_3</bpmn:incoming>
      <bpmn:outgoing>Flow_4</bpmn:outgoing>
    </bpmn:userTask>
    <bpmn:userTask id="ApprovalManager" name="Approval Manager">
      <bpmn:incoming>Flow_4</bpmn:incoming>
      <bpmn:outgoing>Flow_5</bpmn:outgoing>
      <bpmn:outgoing>Flow_6</bpmn:outgoing>
    </bpmn:userTask>
    <bpmn:endEvent id="EndApproved" name="Disetujui">
      <bpmn:incoming>Flow_5</bpmn:incoming>
    </bpmn:endEvent>
    <bpmn:endEvent id="EndRejected" name="Ditolak">
      <bpmn:incoming>Flow_6</bpmn:incoming>
    </bpmn:endEvent>
    <bpmn:sequenceFlow id="Flow_1" sourceRef="StartEvent_1" targetRef="FormBorrower" />
    <bpmn:sequenceFlow id="Flow_2" sourceRef="FormBorrower" targetRef="FormFacility" />
    <bpmn:sequenceFlow id="Flow_3" sourceRef="FormFacility" targetRef="FormFinancial" />
    <bpmn:sequenceFlow id="Flow_4" sourceRef="FormFinancial" targetRef="ApprovalManager" />
    <bpmn:sequenceFlow id="Flow_5" name="approved" sourceRef="ApprovalManager" targetRef="EndApproved" />
    <bpmn:sequenceFlow id="Flow_6" name="rejected" sourceRef="ApprovalManager" targetRef="EndRejected" />
  </bpmn:process>
  <bpmndi:BPMNDiagram id="BPMNDiagram_1">
    <bpmndi:BPMNPlane id="BPMNPlane_1" bpmnElement="Process_1">
      <bpmndi:BPMNShape id="_BPMNShape_StartEvent" bpmnElement="StartEvent_1">
        <dc:Bounds x="100" y="120" width="36" height="36" />
      </bpmndi:BPMNShape>
      <bpmndi:BPMNShape id="FormBorrower_di" bpmnElement="FormBorrower">
        <dc:Bounds x="180" y="98" width="100" height="80" />
      </bpmndi:BPMNShape>
      <bpmndi:BPMNShape id="FormFacility_di" bpmnElement="FormFacility">
        <dc:Bounds x="320" y="98" width="100" height="80" />
      </bpmndi:BPMNShape>
      <bpmndi:BPMNShape id="FormFinancial_di" bpmnElement="FormFinancial">
        <dc:Bounds x="460" y="98" width="100" height="80" />
      </bpmndi:BPMNShape>
      <bpmndi:BPMNShape id="ApprovalManager_di" bpmnElement="ApprovalManager">
        <dc:Bounds x="600" y="98" width="100" height="80" />
      </bpmndi:BPMNShape>
      <bpmndi:BPMNShape id="EndApproved_di" bpmnElement="EndApproved">
        <dc:Bounds x="750" y="80" width="36" height="36" />
      </bpmndi:BPMNShape>
      <bpmndi:BPMNShape id="EndRejected_di" bpmnElement="EndRejected">
        <dc:Bounds x="750" y="160" width="36" height="36" />
      </bpmndi:BPMNShape>
      <bpmndi:BPMNEdge id="Flow_1_di" bpmnElement="Flow_1">
        <di:waypoint x="136" y="138" />
        <di:waypoint x="180" y="138" />
      </bpmndi:BPMNEdge>
      <bpmndi:BPMNEdge id="Flow_2_di" bpmnElement="Flow_2">
        <di:waypoint x="280" y="138" />
        <di:waypoint x="320" y="138" />
      </bpmndi:BPMNEdge>
      <bpmndi:BPMNEdge id="Flow_3_di" bpmnElement="Flow_3">
        <di:waypoint x="420" y="138" />
        <di:waypoint x="460" y="138" />
      </bpmndi:BPMNEdge>
      <bpmndi:BPMNEdge id="Flow_4_di" bpmnElement="Flow_4">
        <di:waypoint x="560" y="138" />
        <di:waypoint x="600" y="138" />
      </bpmndi:BPMNEdge>
      <bpmndi:BPMNEdge id="Flow_5_di" bpmnElement="Flow_5">
        <di:waypoint x="700" y="118" />
        <di:waypoint x="750" y="98" />
      </bpmndi:BPMNEdge>
      <bpmndi:BPMNEdge id="Flow_6_di" bpmnElement="Flow_6">
        <di:waypoint x="700" y="158" />
        <di:waypoint x="750" y="178" />
      </bpmndi:BPMNEdge>
    </bpmndi:BPMNPlane>
  </bpmndi:BPMNDiagram>
</bpmn:definitions>`,
    elementConfigs: {
      StartEvent_1: {
        nodeType: 'StartNode',
        label: 'Mulai',
        description: 'Titik awal',
        config: { triggerType: 'manual', applicableProducts: [], applicablePersonas: [] },
        actions: []
      },
      FormBorrower: {
        nodeType: 'FormNode',
        label: 'Data Pemohon',
        description: 'Input data diri pemohon kredit',
        config: {
          formTemplate: '',
          sections: [
            {
              sectionId: 'sec_borrower',
              label: 'Identitas Pemohon',
              collapsed: false,
              order: 1,
              visible: true
            },
            {
              sectionId: 'sec_employer',
              label: 'Pekerjaan & NPWP',
              collapsed: false,
              order: 2,
              visible: true
            }
          ],
          fields: [
            { fieldname: 'borrower_name', label: 'Nama Pemohon', visible: true, mandatory: true, readOnly: false, defaultValue: '', placement: 'sec_borrower', order: 1 },
            { fieldname: 'borrower_type', label: 'Tipe Pemohon', visible: true, mandatory: true, readOnly: false, defaultValue: '', placement: 'sec_borrower', order: 2 },
            { fieldname: 'industry', label: 'Industri', visible: true, mandatory: false, readOnly: false, defaultValue: '', placement: 'sec_borrower', order: 3 },
            { fieldname: 'kbli', label: 'KBLI', visible: true, mandatory: false, readOnly: false, defaultValue: '', placement: 'sec_borrower', order: 4 },
            { fieldname: 'employer_name', label: 'Perusahaan', visible: true, mandatory: false, readOnly: false, defaultValue: '', placement: 'sec_employer', order: 1 },
            { fieldname: 'npwp', label: 'NPWP', visible: true, mandatory: false, readOnly: false, defaultValue: '', placement: 'sec_employer', order: 2 },
          ],
          availableActions: ['save_draft', 'submit']
        },
        actions: []
      },
      FormFacility: {
        nodeType: 'FormNode',
        label: 'Data Fasilitas',
        description: 'Input detail fasilitas kredit',
        config: {
          formTemplate: '',
          sections: [
            {
              sectionId: 'sec_facility',
              label: 'Fasilitas Kredit',
              collapsed: false,
              order: 1,
              visible: true
            },
            {
              sectionId: 'sec_collateral',
              label: 'Agunan',
              collapsed: false,
              order: 2,
              visible: true
            }
          ],
          fields: [
            { fieldname: 'facility_type', label: 'Jenis Fasilitas', visible: true, mandatory: true, readOnly: false, defaultValue: '', placement: 'sec_facility', order: 1 },
            { fieldname: 'requested_amount', label: 'Jumlah Dimohon', visible: true, mandatory: true, readOnly: false, defaultValue: '', placement: 'sec_facility', order: 2 },
            { fieldname: 'tenor_months', label: 'Tenor (Bulan)', visible: true, mandatory: false, readOnly: false, defaultValue: '', placement: 'sec_facility', order: 3 },
            { fieldname: 'interest_rate', label: 'Suku Bunga (% p.a.)', visible: true, mandatory: false, readOnly: false, defaultValue: '', placement: 'sec_facility', order: 4 },
            { fieldname: 'repayment_scheme', label: 'Skema Pembayaran', visible: true, mandatory: false, readOnly: false, defaultValue: '', placement: 'sec_facility', order: 5 },
            { fieldname: 'collateral_type', label: 'Jenis Agunan', visible: true, mandatory: false, readOnly: false, defaultValue: '', placement: 'sec_collateral', order: 1 },
            { fieldname: 'collateral_value', label: 'Nilai Agunan', visible: true, mandatory: false, readOnly: false, defaultValue: '', placement: 'sec_collateral', order: 2 },
          ],
          availableActions: ['save_draft', 'submit']
        },
        actions: []
      },
      FormFinancial: {
        nodeType: 'FormNode',
        label: 'Data Keuangan',
        description: 'Input ringkasan keuangan pemohon',
        config: {
          formTemplate: '',
          sections: [
            {
              sectionId: 'sec_financial',
              label: 'Ringkasan Keuangan',
              collapsed: false,
              order: 1,
              visible: true
            }
          ],
          fields: [
            { fieldname: 'revenue', label: 'Pendapatan', visible: true, mandatory: false, readOnly: false, defaultValue: '', placement: 'sec_financial', order: 1 },
            { fieldname: 'ebitda', label: 'EBITDA', visible: true, mandatory: false, readOnly: false, defaultValue: '', placement: 'sec_financial', order: 2 },
            { fieldname: 'net_profit', label: 'Laba Bersih', visible: true, mandatory: false, readOnly: false, defaultValue: '', placement: 'sec_financial', order: 3 },
            { fieldname: 'total_assets', label: 'Total Aset', visible: true, mandatory: false, readOnly: false, defaultValue: '', placement: 'sec_financial', order: 4 },
            { fieldname: 'total_liabilities', label: 'Total Liabilitas', visible: true, mandatory: false, readOnly: false, defaultValue: '', placement: 'sec_financial', order: 5 },
            { fieldname: 'equity', label: 'Ekuitas', visible: true, mandatory: false, readOnly: false, defaultValue: '', placement: 'sec_financial', order: 6 },
          ],
          availableActions: ['save_draft', 'submit']
        },
        actions: []
      },
      ApprovalManager: {
        nodeType: 'ApprovalNode',
        label: 'Approval Manager',
        description: 'Persetujuan oleh Manager',
        config: {
          approvalType: 'single',
          approvers: [{ role: 'Manager' }],
          availableActions: ['approve', 'reject', 'return']
        },
        actions: []
      },
      EndApproved: {
        nodeType: 'EndNode',
        label: 'Disetujui',
        description: 'Kredit disetujui',
        config: { outcome: 'approved', finalActions: [], notifications: [] },
        actions: []
      },
      EndRejected: {
        nodeType: 'EndNode',
        label: 'Ditolak',
        description: 'Kredit ditolak',
        config: { outcome: 'rejected', finalActions: [], notifications: [] },
        actions: []
      }
    },
    nodes: [
      {
        id: 'StartEvent_1',
        type: 'creditNode',
        position: { x: 100, y: 120 },
        data: {
          nodeType: 'StartNode',
          label: 'Mulai',
          description: 'Titik awal',
          config: { triggerType: 'manual', applicableProducts: [], applicablePersonas: [] },
          actions: []
        }
      },
      {
        id: 'FormBorrower',
        type: 'creditNode',
        position: { x: 180, y: 98 },
        data: {
          nodeType: 'FormNode',
          label: 'Data Pemohon',
          description: 'Input data diri pemohon kredit',
          config: {
            formTemplate: '',
            sections: [
              { sectionId: 'sec_borrower', label: 'Identitas Pemohon', collapsed: false, order: 1, visible: true },
              { sectionId: 'sec_employer', label: 'Pekerjaan & NPWP', collapsed: false, order: 2, visible: true }
            ],
            fields: [
              { fieldname: 'borrower_name', label: 'Nama Pemohon', visible: true, mandatory: true, readOnly: false, defaultValue: '', placement: 'sec_borrower', order: 1 },
              { fieldname: 'borrower_type', label: 'Tipe Pemohon', visible: true, mandatory: true, readOnly: false, defaultValue: '', placement: 'sec_borrower', order: 2 },
              { fieldname: 'industry', label: 'Industri', visible: true, mandatory: false, readOnly: false, defaultValue: '', placement: 'sec_borrower', order: 3 },
              { fieldname: 'kbli', label: 'KBLI', visible: true, mandatory: false, readOnly: false, defaultValue: '', placement: 'sec_borrower', order: 4 },
              { fieldname: 'employer_name', label: 'Perusahaan', visible: true, mandatory: false, readOnly: false, defaultValue: '', placement: 'sec_employer', order: 1 },
              { fieldname: 'npwp', label: 'NPWP', visible: true, mandatory: false, readOnly: false, defaultValue: '', placement: 'sec_employer', order: 2 },
            ],
            availableActions: ['save_draft', 'submit']
          },
          actions: []
        }
      },
      {
        id: 'FormFacility',
        type: 'creditNode',
        position: { x: 320, y: 98 },
        data: {
          nodeType: 'FormNode',
          label: 'Data Fasilitas',
          description: 'Input detail fasilitas kredit',
          config: {
            formTemplate: '',
            sections: [
              { sectionId: 'sec_facility', label: 'Fasilitas Kredit', collapsed: false, order: 1, visible: true },
              { sectionId: 'sec_collateral', label: 'Agunan', collapsed: false, order: 2, visible: true }
            ],
            fields: [
              { fieldname: 'facility_type', label: 'Jenis Fasilitas', visible: true, mandatory: true, readOnly: false, defaultValue: '', placement: 'sec_facility', order: 1 },
              { fieldname: 'requested_amount', label: 'Jumlah Dimohon', visible: true, mandatory: true, readOnly: false, defaultValue: '', placement: 'sec_facility', order: 2 },
              { fieldname: 'tenor_months', label: 'Tenor (Bulan)', visible: true, mandatory: false, readOnly: false, defaultValue: '', placement: 'sec_facility', order: 3 },
              { fieldname: 'interest_rate', label: 'Suku Bunga (% p.a.)', visible: true, mandatory: false, readOnly: false, defaultValue: '', placement: 'sec_facility', order: 4 },
              { fieldname: 'repayment_scheme', label: 'Skema Pembayaran', visible: true, mandatory: false, readOnly: false, defaultValue: '', placement: 'sec_facility', order: 5 },
              { fieldname: 'collateral_type', label: 'Jenis Agunan', visible: true, mandatory: false, readOnly: false, defaultValue: '', placement: 'sec_collateral', order: 1 },
              { fieldname: 'collateral_value', label: 'Nilai Agunan', visible: true, mandatory: false, readOnly: false, defaultValue: '', placement: 'sec_collateral', order: 2 },
            ],
            availableActions: ['save_draft', 'submit']
          },
          actions: []
        }
      },
      {
        id: 'FormFinancial',
        type: 'creditNode',
        position: { x: 460, y: 98 },
        data: {
          nodeType: 'FormNode',
          label: 'Data Keuangan',
          description: 'Input ringkasan keuangan pemohon',
          config: {
            formTemplate: '',
            sections: [
              { sectionId: 'sec_financial', label: 'Ringkasan Keuangan', collapsed: false, order: 1, visible: true }
            ],
            fields: [
              { fieldname: 'revenue', label: 'Pendapatan', visible: true, mandatory: false, readOnly: false, defaultValue: '', placement: 'sec_financial', order: 1 },
              { fieldname: 'ebitda', label: 'EBITDA', visible: true, mandatory: false, readOnly: false, defaultValue: '', placement: 'sec_financial', order: 2 },
              { fieldname: 'net_profit', label: 'Laba Bersih', visible: true, mandatory: false, readOnly: false, defaultValue: '', placement: 'sec_financial', order: 3 },
              { fieldname: 'total_assets', label: 'Total Aset', visible: true, mandatory: false, readOnly: false, defaultValue: '', placement: 'sec_financial', order: 4 },
              { fieldname: 'total_liabilities', label: 'Total Liabilitas', visible: true, mandatory: false, readOnly: false, defaultValue: '', placement: 'sec_financial', order: 5 },
              { fieldname: 'equity', label: 'Ekuitas', visible: true, mandatory: false, readOnly: false, defaultValue: '', placement: 'sec_financial', order: 6 },
            ],
            availableActions: ['save_draft', 'submit']
          },
          actions: []
        }
      },
      {
        id: 'ApprovalManager',
        type: 'creditNode',
        position: { x: 600, y: 98 },
        data: {
          nodeType: 'ApprovalNode',
          label: 'Approval Manager',
          description: 'Persetujuan oleh Manager',
          config: {
            approvalType: 'single',
            approvers: [{ role: 'Manager' }],
            availableActions: ['approve', 'reject', 'return']
          },
          actions: []
        }
      },
      {
        id: 'EndApproved',
        type: 'creditNode',
        position: { x: 750, y: 80 },
        data: {
          nodeType: 'EndNode',
          label: 'Disetujui',
          description: 'Kredit disetujui',
          config: { outcome: 'approved', finalActions: [], notifications: [] },
          actions: []
        }
      },
      {
        id: 'EndRejected',
        type: 'creditNode',
        position: { x: 750, y: 160 },
        data: {
          nodeType: 'EndNode',
          label: 'Ditolak',
          description: 'Kredit ditolak',
          config: { outcome: 'rejected', finalActions: [], notifications: [] },
          actions: []
        }
      }
    ],
    edges: [
      {
        id: 'Flow_1',
        source: 'StartEvent_1',
        target: 'FormBorrower',
        sourceHandle: 'Flow_1',
        label: '',
        data: { label: '' }
      },
      {
        id: 'Flow_2',
        source: 'FormBorrower',
        target: 'FormFacility',
        sourceHandle: 'Flow_2',
        label: '',
        data: { label: '' }
      },
      {
        id: 'Flow_3',
        source: 'FormFacility',
        target: 'FormFinancial',
        sourceHandle: 'Flow_3',
        label: '',
        data: { label: '' }
      },
      {
        id: 'Flow_4',
        source: 'FormFinancial',
        target: 'ApprovalManager',
        sourceHandle: 'Flow_4',
        label: '',
        data: { label: '' }
      },
      {
        id: 'Flow_5',
        source: 'ApprovalManager',
        target: 'EndApproved',
        sourceHandle: 'approved',
        label: 'approved',
        data: { label: 'approved' }
      },
      {
        id: 'Flow_6',
        source: 'ApprovalManager',
        target: 'EndRejected',
        sourceHandle: 'rejected',
        label: 'rejected',
        data: { label: 'rejected' }
      }
    ]
  },
  {
    id: 'blank',
    title: 'Kanvas Kosong',
    description: 'Mulai dari awal dan rancang alur kerja kustom Anda sendiri dengan kanvas kosong.',
    icon: 'LucideFile',
    color: 'from-gray-400 to-gray-500',
    marketplaceCategory: 'Custom',
    xml: `<?xml version="1.0" encoding="UTF-8"?>
<bpmn:definitions xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" 
                  xmlns:bpmn="http://www.omg.org/spec/BPMN/20100524/MODEL" 
                  xmlns:bpmndi="http://www.omg.org/spec/BPMN/20100524/DI" 
                  xmlns:dc="http://www.omg.org/spec/DD/20100524/DC" 
                  xmlns:di="http://www.omg.org/spec/DD/20100524/DI" 
                  id="Definitions_1" 
                  targetNamespace="http://bpmn.io/schema/bpmn">
  <bpmn:process id="Process_1" isExecutable="true">
    <bpmn:startEvent id="StartEvent_1" name="Mulai">
      <bpmn:outgoing>Flow_1</bpmn:outgoing>
    </bpmn:startEvent>
    <bpmn:endEvent id="EndEvent_1" name="Selesai">
      <bpmn:incoming>Flow_1</bpmn:incoming>
    </bpmn:endEvent>
    <bpmn:sequenceFlow id="Flow_1" sourceRef="StartEvent_1" targetRef="EndEvent_1" />
  </bpmn:process>
  <bpmndi:BPMNDiagram id="BPMNDiagram_1">
    <bpmndi:BPMNPlane id="BPMNPlane_1" bpmnElement="Process_1">
      <bpmndi:BPMNShape id="_BPMNShape_StartEvent_2" bpmnElement="StartEvent_1">
        <dc:Bounds x="173" y="102" width="36" height="36" />
      </bpmndi:BPMNShape>
      <bpmndi:BPMNShape id="EndEvent_1_di" bpmnElement="EndEvent_1">
        <dc:Bounds x="370" y="102" width="36" height="36" />
      </bpmndi:BPMNShape>
      <bpmndi:BPMNEdge id="Flow_1_di" bpmnElement="Flow_1">
        <di:waypoint x="209" y="120" />
        <di:waypoint x="370" y="120" />
      </bpmndi:BPMNEdge>
    </bpmndi:BPMNPlane>
  </bpmndi:BPMNDiagram>
</bpmn:definitions>`,
    elementConfigs: {},
    nodes: [
      {
        id: 'StartEvent_1',
        type: 'creditNode',
        position: { x: 173, y: 102 },
        data: {
          nodeType: 'StartNode',
          label: 'Mulai',
          description: 'Titik awal',
          config: { triggerType: 'manual', applicableProducts: [], applicablePersonas: [] },
          actions: []
        }
      },
      {
        id: 'EndEvent_1',
        type: 'creditNode',
        position: { x: 370, y: 102 },
        data: {
          nodeType: 'EndNode',
          label: 'Selesai',
          description: 'Selesai',
          config: { outcome: 'approved', finalActions: [], notifications: [] },
          actions: []
        }
      }
    ],
    edges: [
      {
        id: 'Flow_1',
        source: 'StartEvent_1',
        target: 'EndEvent_1',
        sourceHandle: 'Flow_1',
        label: '',
        data: { label: '' }
      }
    ]
  },
  {
    id: 'lead_qual',
    title: 'Kualifikasi & Pengisian Data Prospek',
    description: 'Alur kerja standar untuk mengumpulkan data prospek melalui Form Stage sebelum otomatis selesai.',
    icon: 'LucideUserCheck',
    color: 'from-blue-500 to-indigo-500',
    marketplaceCategory: 'Lead Management',
    xml: `<?xml version="1.0" encoding="UTF-8"?>
<bpmn:definitions xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" 
                  xmlns:bpmn="http://www.omg.org/spec/BPMN/20100524/MODEL" 
                  xmlns:bpmndi="http://www.omg.org/spec/BPMN/20100524/DI" 
                  xmlns:dc="http://www.omg.org/spec/DD/20100524/DC" 
                  xmlns:di="http://www.omg.org/spec/DD/20100524/DI" 
                  id="Definitions_1" 
                  targetNamespace="http://bpmn.io/schema/bpmn">
  <bpmn:process id="Process_1" isExecutable="true">
    <bpmn:startEvent id="StartEvent_1" name="Mulai">
      <bpmn:outgoing>Flow_1</bpmn:outgoing>
    </bpmn:startEvent>
    <bpmn:userTask id="FormNode_1" name="Input Data">
      <bpmn:incoming>Flow_1</bpmn:incoming>
      <bpmn:outgoing>Flow_2</bpmn:outgoing>
    </bpmn:userTask>
    <bpmn:endEvent id="EndEvent_1" name="Selesai">
      <bpmn:incoming>Flow_2</bpmn:incoming>
    </bpmn:endEvent>
    <bpmn:sequenceFlow id="Flow_1" sourceRef="StartEvent_1" targetRef="FormNode_1" />
    <bpmn:sequenceFlow id="Flow_2" sourceRef="FormNode_1" targetRef="EndEvent_1" />
  </bpmn:process>
  <bpmndi:BPMNDiagram id="BPMNDiagram_1">
    <bpmndi:BPMNPlane id="BPMNPlane_1" bpmnElement="Process_1">
      <bpmndi:BPMNShape id="_BPMNShape_StartEvent_2" bpmnElement="StartEvent_1">
        <dc:Bounds x="173" y="102" width="36" height="36" />
      </bpmndi:BPMNShape>
      <bpmndi:BPMNShape id="FormNode_1_di" bpmnElement="FormNode_1">
        <dc:Bounds x="250" y="80" width="100" height="80" />
      </bpmndi:BPMNShape>
      <bpmndi:BPMNShape id="EndEvent_1_di" bpmnElement="EndEvent_1">
        <dc:Bounds x="400" y="102" width="36" height="36" />
      </bpmndi:BPMNShape>
      <bpmndi:BPMNEdge id="Flow_1_di" bpmnElement="Flow_1">
        <di:waypoint x="209" y="120" />
        <di:waypoint x="250" y="120" />
      </bpmndi:BPMNEdge>
      <bpmndi:BPMNEdge id="Flow_2_di" bpmnElement="Flow_2">
        <di:waypoint x="350" y="120" />
        <di:waypoint x="400" y="120" />
      </bpmndi:BPMNEdge>
    </bpmndi:BPMNPlane>
  </bpmndi:BPMNDiagram>
</bpmn:definitions>`,
    elementConfigs: {
      StartEvent_1: {
        nodeType: 'StartNode',
        label: 'Mulai',
        description: 'Titik awal',
        config: { triggerType: 'manual', applicableProducts: [], applicablePersonas: [] },
        actions: []
      },
      FormNode_1: {
        nodeType: 'FormNode',
        label: 'Input Data',
        description: 'Pengisian data prospek',
        config: {
          formTemplate: '',
          sections: [
            {
              id: 'sec_1',
              title: 'Data Utama',
              fields: ['first_name', 'last_name', 'email', 'mobile_no']
            }
          ],
          fields: [
            { fieldname: 'first_name', label: 'Nama Depan', fieldtype: 'Data', reqd: 1 },
            { fieldname: 'last_name', label: 'Nama Belakang', fieldtype: 'Data' },
            { fieldname: 'email', label: 'Email', fieldtype: 'Data', reqd: 1 },
            { fieldname: 'mobile_no', label: 'Nomor Handphone', fieldtype: 'Data', reqd: 1 }
          ],
          availableActions: ['submit']
        },
        actions: []
      },
      EndEvent_1: {
        nodeType: 'EndNode',
        label: 'Selesai',
        description: 'Selesai',
        config: { outcome: 'approved', finalActions: [], notifications: [] },
        actions: []
      }
    },
    nodes: [
      {
        id: 'StartEvent_1',
        type: 'creditNode',
        position: { x: 173, y: 102 },
        data: {
          nodeType: 'StartNode',
          label: 'Mulai',
          description: 'Titik awal',
          config: { triggerType: 'manual', applicableProducts: [], applicablePersonas: [] },
          actions: []
        }
      },
      {
        id: 'FormNode_1',
        type: 'creditNode',
        position: { x: 250, y: 80 },
        data: {
          nodeType: 'FormNode',
          label: 'Input Data',
          description: 'Pengisian data prospek',
          config: {
            formTemplate: '',
            sections: [
              {
                id: 'sec_1',
                title: 'Data Utama',
                fields: ['first_name', 'last_name', 'email', 'mobile_no']
              }
            ],
            fields: [
              { fieldname: 'first_name', label: 'Nama Depan', fieldtype: 'Data', reqd: 1 },
              { fieldname: 'last_name', label: 'Nama Belakang', fieldtype: 'Data' },
              { fieldname: 'email', label: 'Email', fieldtype: 'Data', reqd: 1 },
              { fieldname: 'mobile_no', label: 'Nomor Handphone', fieldtype: 'Data', reqd: 1 }
            ],
            availableActions: ['submit']
          },
          actions: []
        }
      },
      {
        id: 'EndEvent_1',
        type: 'creditNode',
        position: { x: 400, y: 102 },
        data: {
          nodeType: 'EndNode',
          label: 'Selesai',
          description: 'Selesai',
          config: { outcome: 'approved', finalActions: [], notifications: [] },
          actions: []
        }
      }
    ],
    edges: [
      {
        id: 'Flow_1',
        source: 'StartEvent_1',
        target: 'FormNode_1',
        sourceHandle: 'Flow_1',
        label: '',
        data: { label: '' }
      },
      {
        id: 'Flow_2',
        source: 'FormNode_1',
        target: 'EndEvent_1',
        sourceHandle: 'Flow_2',
        label: '',
        data: { label: '' }
      }
    ]
  },
  {
    id: 'approval_matrix',
    title: 'Persetujuan Manajer Multilevel',
    description: 'Alur kerja persetujuan dengan input data oleh RM dan approval bertingkat.',
    icon: 'LucideShieldCheck',
    color: 'from-emerald-500 to-teal-500',
    marketplaceCategory: 'Approval',
    xml: `<?xml version="1.0" encoding="UTF-8"?>
<bpmn:definitions xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" 
                  xmlns:bpmn="http://www.omg.org/spec/BPMN/20100524/MODEL" 
                  xmlns:bpmndi="http://www.omg.org/spec/BPMN/20100524/DI" 
                  xmlns:dc="http://www.omg.org/spec/DD/20100524/DC" 
                  xmlns:di="http://www.omg.org/spec/DD/20100524/DI" 
                  id="Definitions_1" 
                  targetNamespace="http://bpmn.io/schema/bpmn">
  <bpmn:process id="Process_1" isExecutable="true">
    <bpmn:startEvent id="StartEvent_1" name="Mulai">
      <bpmn:outgoing>Flow_1</bpmn:outgoing>
    </bpmn:startEvent>
    <bpmn:userTask id="FormNode_1" name="Input Data">
      <bpmn:incoming>Flow_1</bpmn:incoming>
      <bpmn:outgoing>Flow_2</bpmn:outgoing>
    </bpmn:userTask>
    <bpmn:userTask id="ApprovalNode_1" name="Persetujuan Manajer">
      <bpmn:incoming>Flow_2</bpmn:incoming>
      <bpmn:outgoing>Flow_3</bpmn:outgoing>
      <bpmn:outgoing>Flow_4</bpmn:outgoing>
    </bpmn:userTask>
    <bpmn:endEvent id="EndEvent_1" name="Diterima">
      <bpmn:incoming>Flow_3</bpmn:incoming>
    </bpmn:endEvent>
    <bpmn:endEvent id="EndEvent_2" name="Ditolak">
      <bpmn:incoming>Flow_4</bpmn:incoming>
    </bpmn:endEvent>
    <bpmn:sequenceFlow id="Flow_1" sourceRef="StartEvent_1" targetRef="FormNode_1" />
    <bpmn:sequenceFlow id="Flow_2" sourceRef="FormNode_1" targetRef="ApprovalNode_1" />
    <bpmn:sequenceFlow id="Flow_3" name="approved" sourceRef="ApprovalNode_1" targetRef="EndEvent_1" />
    <bpmn:sequenceFlow id="Flow_4" name="rejected" sourceRef="ApprovalNode_1" targetRef="EndEvent_2" />
  </bpmn:process>
  <bpmndi:BPMNDiagram id="BPMNDiagram_1">
    <bpmndi:BPMNPlane id="BPMNPlane_1" bpmnElement="Process_1">
      <bpmndi:BPMNShape id="_BPMNShape_StartEvent_2" bpmnElement="StartEvent_1">
        <dc:Bounds x="173" y="102" width="36" height="36" />
      </bpmndi:BPMNShape>
      <bpmndi:BPMNShape id="FormNode_1_di" bpmnElement="FormNode_1">
        <dc:Bounds x="250" y="80" width="100" height="80" />
      </bpmndi:BPMNShape>
      <bpmndi:BPMNShape id="ApprovalNode_1_di" bpmnElement="ApprovalNode_1">
        <dc:Bounds x="390" y="80" width="100" height="80" />
      </bpmndi:BPMNShape>
      <bpmndi:BPMNShape id="EndEvent_1_di" bpmnElement="EndEvent_1">
        <dc:Bounds x="540" y="72" width="36" height="36" />
      </bpmndi:BPMNShape>
      <bpmndi:BPMNShape id="EndEvent_2_di" bpmnElement="EndEvent_2">
        <dc:Bounds x="540" y="152" width="36" height="36" />
      </bpmndi:BPMNShape>
      <bpmndi:BPMNEdge id="Flow_1_di" bpmnElement="Flow_1">
        <di:waypoint x="209" y="120" />
        <di:waypoint x="250" y="120" />
      </bpmndi:BPMNEdge>
      <bpmndi:BPMNEdge id="Flow_2_di" bpmnElement="Flow_2">
        <di:waypoint x="350" y="120" />
        <di:waypoint x="390" y="120" />
      </bpmndi:BPMNEdge>
      <bpmndi:BPMNEdge id="Flow_3_di" bpmnElement="Flow_3">
        <di:waypoint x="490" y="110" />
        <di:waypoint x="540" y="90" />
      </bpmndi:BPMNEdge>
      <bpmndi:BPMNEdge id="Flow_4_di" bpmnElement="Flow_4">
        <di:waypoint x="490" y="130" />
        <di:waypoint x="540" y="170" />
      </bpmndi:BPMNEdge>
    </bpmndi:BPMNPlane>
  </bpmndi:BPMNDiagram>
</bpmn:definitions>`,
    elementConfigs: {
      StartEvent_1: {
        nodeType: 'StartNode',
        label: 'Mulai',
        description: 'Titik awal',
        config: { triggerType: 'manual', applicableProducts: [], applicablePersonas: [] },
        actions: []
      },
      FormNode_1: {
        nodeType: 'FormNode',
        label: 'Input Data',
        description: 'Pengisian data prospek',
        config: {
          formTemplate: '',
          sections: [
            {
              id: 'sec_1',
              title: 'Data Prospek',
              fields: ['first_name', 'last_name', 'email', 'mobile_no']
            }
          ],
          fields: [
            { fieldname: 'first_name', label: 'Nama Depan', fieldtype: 'Data', reqd: 1 },
            { fieldname: 'last_name', label: 'Nama Belakang', fieldtype: 'Data' },
            { fieldname: 'email', label: 'Email', fieldtype: 'Data', reqd: 1 },
            { fieldname: 'mobile_no', label: 'Nomor Handphone', fieldtype: 'Data', reqd: 1 }
          ],
          availableActions: ['submit']
        },
        actions: []
      },
      ApprovalNode_1: {
        nodeType: 'ApprovalNode',
        label: 'Persetujuan Manajer',
        description: 'Persetujuan oleh Sales Manager',
        config: {
          approvalType: 'single',
          approvers: [{ role: 'Sales Manager' }],
          availableActions: ['approve', 'reject', 'return']
        },
        actions: []
      },
      EndEvent_1: {
        nodeType: 'EndNode',
        label: 'Diterima',
        description: 'Persetujuan Akhir',
        config: { outcome: 'approved', finalActions: [], notifications: [] },
        actions: []
      },
      EndEvent_2: {
        nodeType: 'EndNode',
        label: 'Ditolak',
        description: 'Ditolak oleh Manajer',
        config: { outcome: 'rejected', finalActions: [], notifications: [] },
        actions: []
      }
    },
    nodes: [
      {
        id: 'StartEvent_1',
        type: 'creditNode',
        position: { x: 173, y: 102 },
        data: {
          nodeType: 'StartNode',
          label: 'Mulai',
          description: 'Titik awal',
          config: { triggerType: 'manual', applicableProducts: [], applicablePersonas: [] },
          actions: []
        }
      },
      {
        id: 'FormNode_1',
        type: 'creditNode',
        position: { x: 250, y: 80 },
        data: {
          nodeType: 'FormNode',
          label: 'Input Data',
          description: 'Pengisian data prospek',
          config: {
            formTemplate: '',
            sections: [
              {
                id: 'sec_1',
                title: 'Data Prospek',
                fields: ['first_name', 'last_name', 'email', 'mobile_no']
              }
            ],
            fields: [
              { fieldname: 'first_name', label: 'Nama Depan', fieldtype: 'Data', reqd: 1 },
              { fieldname: 'last_name', label: 'Nama Belakang', fieldtype: 'Data' },
              { fieldname: 'email', label: 'Email', fieldtype: 'Data', reqd: 1 },
              { fieldname: 'mobile_no', label: 'Nomor Handphone', fieldtype: 'Data', reqd: 1 }
            ],
            availableActions: ['submit']
          },
          actions: []
        }
      },
      {
        id: 'ApprovalNode_1',
        type: 'creditNode',
        position: { x: 390, y: 80 },
        data: {
          nodeType: 'ApprovalNode',
          label: 'Persetujuan Manajer',
          description: 'Persetujuan oleh Sales Manager',
          config: {
            approvalType: 'single',
            approvers: [{ role: 'Sales Manager' }],
            availableActions: ['approve', 'reject', 'return']
          },
          actions: []
        }
      },
      {
        id: 'EndEvent_1',
        type: 'creditNode',
        position: { x: 540, y: 72 },
        data: {
          nodeType: 'EndNode',
          label: 'Diterima',
          description: 'Persetujuan Akhir',
          config: { outcome: 'approved', finalActions: [], notifications: [] },
          actions: []
        }
      },
      {
        id: 'EndEvent_2',
        type: 'creditNode',
        position: { x: 540, y: 152 },
        data: {
          nodeType: 'EndNode',
          label: 'Ditolak',
          description: 'Ditolak oleh Manajer',
          config: { outcome: 'rejected', finalActions: [], notifications: [] },
          actions: []
        }
      }
    ],
    edges: [
      {
        id: 'Flow_1',
        source: 'StartEvent_1',
        target: 'FormNode_1',
        sourceHandle: 'Flow_1',
        label: '',
        data: { label: '' }
      },
      {
        id: 'Flow_2',
        source: 'FormNode_1',
        target: 'ApprovalNode_1',
        sourceHandle: 'Flow_2',
        label: '',
        data: { label: '' }
      },
      {
        id: 'Flow_3',
        source: 'ApprovalNode_1',
        target: 'EndEvent_1',
        sourceHandle: 'approved',
        label: 'approved',
        data: { label: 'approved' }
      },
      {
        id: 'Flow_4',
        source: 'ApprovalNode_1',
        target: 'EndEvent_2',
        sourceHandle: 'rejected',
        label: 'rejected',
        data: { label: 'rejected' }
      }
    ]
  },
  {
    id: 'credit_approval_full',
    title: 'Persetujuan Kredit Lengkap',
    description: 'Alur persetujuan kredit lengkap: data pemohon, fasilitas, keuangan, SLA review, keputusan jumlah, approval Branch Manager & Regional Manager.',
    icon: 'LucideShieldCheck',
    color: 'from-green-500 to-emerald-600',
    xml: `<?xml version="1.0" encoding="UTF-8"?>
<bpmn:definitions xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"
                  xmlns:bpmn="http://www.omg.org/spec/BPMN/20100524/MODEL"
                  xmlns:bpmndi="http://www.omg.org/spec/BPMN/20100524/DI"
                  xmlns:dc="http://www.omg.org/spec/DD/20100524/DC"
                  xmlns:di="http://www.omg.org/spec/DD/20100524/DI"
                  id="Definitions_1"
                  targetNamespace="http://bpmn.io/schema/bpmn">
  <bpmn:process id="Process_1" isExecutable="true">
    <bpmn:startEvent id="StartEvent_1" name="Mulai">
      <bpmn:outgoing>Flow_1</bpmn:outgoing>
    </bpmn:startEvent>
    <bpmn:userTask id="FormBorrower" name="Data Pemohon">
      <bpmn:incoming>Flow_1</bpmn:incoming>
      <bpmn:outgoing>Flow_2</bpmn:outgoing>
    </bpmn:userTask>
    <bpmn:userTask id="FormFacility" name="Data Fasilitas">
      <bpmn:incoming>Flow_2</bpmn:incoming>
      <bpmn:outgoing>Flow_3</bpmn:outgoing>
    </bpmn:userTask>
    <bpmn:userTask id="FormFinancial" name="Data Keuangan">
      <bpmn:incoming>Flow_3</bpmn:incoming>
      <bpmn:outgoing>Flow_4</bpmn:outgoing>
    </bpmn:userTask>
    <bpmn:serviceTask id="SLAReview" name="SLA Review">
      <bpmn:incoming>Flow_4</bpmn:incoming>
      <bpmn:outgoing>Flow_5</bpmn:outgoing>
    </bpmn:serviceTask>
    <bpmn:exclusiveGateway id="DecisionAmount" name="Cek Jumlah">
      <bpmn:incoming>Flow_5</bpmn:incoming>
      <bpmn:outgoing>Flow_6</bpmn:outgoing>
      <bpmn:outgoing>Flow_Reject1</bpmn:outgoing>
    </bpmn:exclusiveGateway>
    <bpmn:userTask id="ApprovalBM" name="Approval Branch Manager">
      <bpmn:incoming>Flow_6</bpmn:incoming>
      <bpmn:outgoing>Flow_7</bpmn:outgoing>
      <bpmn:outgoing>Flow_Reject2</bpmn:outgoing>
    </bpmn:userTask>
    <bpmn:userTask id="ApprovalRM" name="Approval Regional Manager">
      <bpmn:incoming>Flow_7</bpmn:incoming>
      <bpmn:outgoing>Flow_8</bpmn:outgoing>
      <bpmn:outgoing>Flow_Reject3</bpmn:outgoing>
    </bpmn:userTask>
    <bpmn:endEvent id="EndApproved" name="Disetujui">
      <bpmn:incoming>Flow_8</bpmn:incoming>
    </bpmn:endEvent>
    <bpmn:endEvent id="EndRejected" name="Ditolak">
      <bpmn:incoming>Flow_Reject1</bpmn:incoming>
      <bpmn:incoming>Flow_Reject2</bpmn:incoming>
      <bpmn:incoming>Flow_Reject3</bpmn:incoming>
    </bpmn:endEvent>
    <bpmn:sequenceFlow id="Flow_1" sourceRef="StartEvent_1" targetRef="FormBorrower" />
    <bpmn:sequenceFlow id="Flow_2" sourceRef="FormBorrower" targetRef="FormFacility" />
    <bpmn:sequenceFlow id="Flow_3" sourceRef="FormFacility" targetRef="FormFinancial" />
    <bpmn:sequenceFlow id="Flow_4" sourceRef="FormFinancial" targetRef="SLAReview" />
    <bpmn:sequenceFlow id="Flow_5" sourceRef="SLAReview" targetRef="DecisionAmount" />
    <bpmn:sequenceFlow id="Flow_6" name="amount &lt;= 5B" sourceRef="DecisionAmount" targetRef="ApprovalBM" />
    <bpmn:sequenceFlow id="Flow_Reject1" name="rejected" sourceRef="DecisionAmount" targetRef="EndRejected" />
    <bpmn:sequenceFlow id="Flow_7" name="amount > 5B" sourceRef="ApprovalBM" targetRef="ApprovalRM" />
    <bpmn:sequenceFlow id="Flow_Reject2" name="rejected" sourceRef="ApprovalBM" targetRef="EndRejected" />
    <bpmn:sequenceFlow id="Flow_8" name="approved" sourceRef="ApprovalRM" targetRef="EndApproved" />
    <bpmn:sequenceFlow id="Flow_Reject3" name="rejected" sourceRef="ApprovalRM" targetRef="EndRejected" />
  </bpmn:process>
  <bpmndi:BPMNDiagram id="BPMNDiagram_1">
    <bpmndi:BPMNPlane id="BPMNPlane_1" bpmnElement="Process_1">
      <bpmndi:BPMNShape id="_BPMNShape_StartEvent" bpmnElement="StartEvent_1">
        <dc:Bounds x="100" y="150" width="36" height="36" />
      </bpmndi:BPMNShape>
      <bpmndi:BPMNShape id="FormBorrower_di" bpmnElement="FormBorrower">
        <dc:Bounds x="200" y="128" width="100" height="80" />
      </bpmndi:BPMNShape>
      <bpmndi:BPMNShape id="FormFacility_di" bpmnElement="FormFacility">
        <dc:Bounds x="340" y="128" width="100" height="80" />
      </bpmndi:BPMNShape>
      <bpmndi:BPMNShape id="FormFinancial_di" bpmnElement="FormFinancial">
        <dc:Bounds x="480" y="128" width="100" height="80" />
      </bpmndi:BPMNShape>
      <bpmndi:BPMNShape id="SLAReview_di" bpmnElement="SLAReview">
        <dc:Bounds x="620" y="128" width="100" height="80" />
      </bpmndi:BPMNShape>
      <bpmndi:BPMNShape id="DecisionAmount_di" bpmnElement="DecisionAmount" isMarkerVisible="true">
        <dc:Bounds x="760" y="128" width="50" height="50" />
      </bpmndi:BPMNShape>
      <bpmndi:BPMNShape id="ApprovalBM_di" bpmnElement="ApprovalBM">
        <dc:Bounds x="900" y="80" width="100" height="80" />
      </bpmndi:BPMNShape>
      <bpmndi:BPMNShape id="ApprovalRM_di" bpmnElement="ApprovalRM">
        <dc:Bounds x="1040" y="80" width="100" height="80" />
      </bpmndi:BPMNShape>
      <bpmndi:BPMNShape id="EndApproved_di" bpmnElement="EndApproved">
        <dc:Bounds x="1180" y="60" width="36" height="36" />
      </bpmndi:BPMNShape>
      <bpmndi:BPMNShape id="EndRejected_di" bpmnElement="EndRejected">
        <dc:Bounds x="900" y="250" width="36" height="36" />
      </bpmndi:BPMNShape>
      <bpmndi:BPMNEdge id="Flow_1_di" bpmnElement="Flow_1">
        <di:waypoint x="136" y="168" />
        <di:waypoint x="200" y="168" />
      </bpmndi:BPMNEdge>
      <bpmndi:BPMNEdge id="Flow_2_di" bpmnElement="Flow_2">
        <di:waypoint x="300" y="168" />
        <di:waypoint x="340" y="168" />
      </bpmndi:BPMNEdge>
      <bpmndi:BPMNEdge id="Flow_3_di" bpmnElement="Flow_3">
        <di:waypoint x="440" y="168" />
        <di:waypoint x="480" y="168" />
      </bpmndi:BPMNEdge>
      <bpmndi:BPMNEdge id="Flow_4_di" bpmnElement="Flow_4">
        <di:waypoint x="580" y="168" />
        <di:waypoint x="620" y="168" />
      </bpmndi:BPMNEdge>
      <bpmndi:BPMNEdge id="Flow_5_di" bpmnElement="Flow_5">
        <di:waypoint x="720" y="168" />
        <di:waypoint x="760" y="153" />
      </bpmndi:BPMNEdge>
      <bpmndi:BPMNEdge id="Flow_6_di" bpmnElement="Flow_6">
        <di:waypoint x="810" y="153" />
        <di:waypoint x="900" y="120" />
      </bpmndi:BPMNEdge>
      <bpmndi:BPMNEdge id="Flow_Reject1_di" bpmnElement="Flow_Reject1">
        <di:waypoint x="785" y="178" />
        <di:waypoint x="900" y="268" />
      </bpmndi:BPMNEdge>
      <bpmndi:BPMNEdge id="Flow_7_di" bpmnElement="Flow_7">
        <di:waypoint x="1000" y="120" />
        <di:waypoint x="1040" y="120" />
      </bpmndi:BPMNEdge>
      <bpmndi:BPMNEdge id="Flow_Reject2_di" bpmnElement="Flow_Reject2">
        <di:waypoint x="950" y="160" />
        <di:waypoint x="918" y="250" />
      </bpmndi:BPMNEdge>
      <bpmndi:BPMNEdge id="Flow_8_di" bpmnElement="Flow_8">
        <di:waypoint x="1140" y="100" />
        <di:waypoint x="1180" y="78" />
      </bpmndi:BPMNEdge>
      <bpmndi:BPMNEdge id="Flow_Reject3_di" bpmnElement="Flow_Reject3">
        <di:waypoint x="1090" y="160" />
        <di:waypoint x="936" y="250" />
      </bpmndi:BPMNEdge>
    </bpmndi:BPMNPlane>
  </bpmndi:BPMNDiagram>
</bpmn:definitions>`,
    elementConfigs: {
      StartEvent_1: {
        nodeType: 'StartNode',
        label: 'Mulai',
        description: 'Titik awal proses kredit',
        config: { triggerType: 'manual', applicableProducts: [], applicablePersonas: [] },
        actions: []
      },
      FormBorrower: {
        nodeType: 'FormNode',
        label: 'Data Pemohon',
        description: 'Input data diri pemohon kredit',
        config: {
          formTemplate: '',
          sections: [
            { sectionId: 'sec_borrower', label: 'Identitas Pemohon', collapsed: false, order: 1, visible: true }
          ],
          fields: [
            { fieldname: 'borrower_name', label: 'Nama Pemohon', visible: true, mandatory: true, readOnly: false, defaultValue: '', placement: 'sec_borrower', order: 1 },
            { fieldname: 'borrower_id', label: 'No. KTP', visible: true, mandatory: true, readOnly: false, defaultValue: '', placement: 'sec_borrower', order: 2 },
            { fieldname: 'borrower_type', label: 'Tipe Pemohon', visible: true, mandatory: true, readOnly: false, defaultValue: '', placement: 'sec_borrower', order: 3 }
          ],
          availableActions: ['save_draft', 'submit']
        },
        actions: []
      },
      FormFacility: {
        nodeType: 'FormNode',
        label: 'Data Fasilitas',
        description: 'Input detail fasilitas kredit',
        config: {
          formTemplate: '',
          sections: [
            { sectionId: 'sec_facility', label: 'Fasilitas Kredit', collapsed: false, order: 1, visible: true }
          ],
          fields: [
            { fieldname: 'facility_type', label: 'Jenis Fasilitas', visible: true, mandatory: true, readOnly: false, defaultValue: '', placement: 'sec_facility', order: 1 },
            { fieldname: 'requested_amount', label: 'Jumlah Dimohon', visible: true, mandatory: true, readOnly: false, defaultValue: '', placement: 'sec_facility', order: 2 },
            { fieldname: 'tenor_months', label: 'Tenor (Bulan)', visible: true, mandatory: false, readOnly: false, defaultValue: '', placement: 'sec_facility', order: 3 }
          ],
          availableActions: ['save_draft', 'submit']
        },
        actions: []
      },
      FormFinancial: {
        nodeType: 'FormNode',
        label: 'Data Keuangan',
        description: 'Input ringkasan keuangan pemohon',
        config: {
          formTemplate: '',
          sections: [
            { sectionId: 'sec_financial', label: 'Ringkasan Keuangan', collapsed: false, order: 1, visible: true }
          ],
          fields: [
            { fieldname: 'revenue', label: 'Pendapatan', visible: true, mandatory: false, readOnly: false, defaultValue: '', placement: 'sec_financial', order: 1 },
            { fieldname: 'net_profit', label: 'Laba Bersih', visible: true, mandatory: false, readOnly: false, defaultValue: '', placement: 'sec_financial', order: 2 },
            { fieldname: 'total_assets', label: 'Total Aset', visible: true, mandatory: false, readOnly: false, defaultValue: '', placement: 'sec_financial', order: 3 }
          ],
          availableActions: ['save_draft', 'submit']
        },
        actions: []
      },
      SLAReview: {
        nodeType: 'SLANode',
        label: 'SLA Review',
        description: 'Batas waktu review dokumen kredit',
        config: {
          deadlineHours: 24,
          warningHours: 20,
          reminderIntervalHours: 4,
          escalationTarget: 'Branch Manager',
          escalationAction: 'reassign',
          businessHoursOnly: true
        },
        actions: []
      },
      DecisionAmount: {
        nodeType: 'DecisionNode',
        label: 'Cek Jumlah',
        description: 'Cek apakah jumlah kredit > 5 Miliar',
        config: {
          conditions: [
            { id: 'cond_lte5b', field: 'requested_amount', operator: '<=', value: '5000000000', label: 'amount <= 5B' },
            { id: 'cond_gt5b', field: 'requested_amount', operator: '>', value: '5000000000', label: 'amount > 5B' }
          ],
          defaultPath: 'rejected'
        },
        actions: []
      },
      ApprovalBM: {
        nodeType: 'ApprovalNode',
        label: 'Approval Branch Manager',
        description: 'Persetujuan oleh Branch Manager',
        config: {
          approvalType: 'single',
          approvers: [{ role: 'Branch Manager' }],
          availableActions: ['approve', 'reject', 'return']
        },
        actions: []
      },
      ApprovalRM: {
        nodeType: 'ApprovalNode',
        label: 'Approval Regional Manager',
        description: 'Persetujuan oleh Regional Manager untuk kredit > 5 Miliar',
        config: {
          approvalType: 'single',
          approvers: [{ role: 'Regional Manager' }],
          availableActions: ['approve', 'reject', 'return']
        },
        actions: []
      },
      EndApproved: {
        nodeType: 'EndNode',
        label: 'Disetujui',
        description: 'Kredit disetujui',
        config: { outcome: 'approved', finalActions: [], notifications: [] },
        actions: []
      },
      EndRejected: {
        nodeType: 'EndNode',
        label: 'Ditolak',
        description: 'Kredit ditolak',
        config: { outcome: 'rejected', finalActions: [], notifications: [] },
        actions: []
      }
    },
    nodes: [
      {
        id: 'StartEvent_1',
        type: 'creditNode',
        position: { x: 100, y: 150 },
        data: {
          nodeType: 'StartNode',
          label: 'Mulai',
          description: 'Titik awal proses kredit',
          config: { triggerType: 'manual', applicableProducts: [], applicablePersonas: [] },
          actions: []
        }
      },
      {
        id: 'FormBorrower',
        type: 'creditNode',
        position: { x: 200, y: 128 },
        data: {
          nodeType: 'FormNode',
          label: 'Data Pemohon',
          description: 'Input data diri pemohon kredit',
          config: {
            formTemplate: '',
            sections: [
              { sectionId: 'sec_borrower', label: 'Identitas Pemohon', collapsed: false, order: 1, visible: true }
            ],
            fields: [
              { fieldname: 'borrower_name', label: 'Nama Pemohon', visible: true, mandatory: true, readOnly: false, defaultValue: '', placement: 'sec_borrower', order: 1 },
              { fieldname: 'borrower_id', label: 'No. KTP', visible: true, mandatory: true, readOnly: false, defaultValue: '', placement: 'sec_borrower', order: 2 },
              { fieldname: 'borrower_type', label: 'Tipe Pemohon', visible: true, mandatory: true, readOnly: false, defaultValue: '', placement: 'sec_borrower', order: 3 }
            ],
            availableActions: ['save_draft', 'submit']
          },
          actions: []
        }
      },
      {
        id: 'FormFacility',
        type: 'creditNode',
        position: { x: 340, y: 128 },
        data: {
          nodeType: 'FormNode',
          label: 'Data Fasilitas',
          description: 'Input detail fasilitas kredit',
          config: {
            formTemplate: '',
            sections: [
              { sectionId: 'sec_facility', label: 'Fasilitas Kredit', collapsed: false, order: 1, visible: true }
            ],
            fields: [
              { fieldname: 'facility_type', label: 'Jenis Fasilitas', visible: true, mandatory: true, readOnly: false, defaultValue: '', placement: 'sec_facility', order: 1 },
              { fieldname: 'requested_amount', label: 'Jumlah Dimohon', visible: true, mandatory: true, readOnly: false, defaultValue: '', placement: 'sec_facility', order: 2 },
              { fieldname: 'tenor_months', label: 'Tenor (Bulan)', visible: true, mandatory: false, readOnly: false, defaultValue: '', placement: 'sec_facility', order: 3 }
            ],
            availableActions: ['save_draft', 'submit']
          },
          actions: []
        }
      },
      {
        id: 'FormFinancial',
        type: 'creditNode',
        position: { x: 480, y: 128 },
        data: {
          nodeType: 'FormNode',
          label: 'Data Keuangan',
          description: 'Input ringkasan keuangan pemohon',
          config: {
            formTemplate: '',
            sections: [
              { sectionId: 'sec_financial', label: 'Ringkasan Keuangan', collapsed: false, order: 1, visible: true }
            ],
            fields: [
              { fieldname: 'revenue', label: 'Pendapatan', visible: true, mandatory: false, readOnly: false, defaultValue: '', placement: 'sec_financial', order: 1 },
              { fieldname: 'net_profit', label: 'Laba Bersih', visible: true, mandatory: false, readOnly: false, defaultValue: '', placement: 'sec_financial', order: 2 },
              { fieldname: 'total_assets', label: 'Total Aset', visible: true, mandatory: false, readOnly: false, defaultValue: '', placement: 'sec_financial', order: 3 }
            ],
            availableActions: ['save_draft', 'submit']
          },
          actions: []
        }
      },
      {
        id: 'SLAReview',
        type: 'creditNode',
        position: { x: 620, y: 128 },
        data: {
          nodeType: 'SLANode',
          label: 'SLA Review',
          description: 'Batas waktu review dokumen kredit',
          config: {
            deadlineHours: 24,
            warningHours: 20,
            reminderIntervalHours: 4,
            escalationTarget: 'Branch Manager',
            escalationAction: 'reassign',
            businessHoursOnly: true
          },
          actions: []
        }
      },
      {
        id: 'DecisionAmount',
        type: 'creditNode',
        position: { x: 760, y: 128 },
        data: {
          nodeType: 'DecisionNode',
          label: 'Cek Jumlah',
          description: 'Cek apakah jumlah kredit > 5 Miliar',
          config: {
            conditions: [
              { id: 'cond_lte5b', field: 'requested_amount', operator: '<=', value: '5000000000', label: 'amount <= 5B' },
              { id: 'cond_gt5b', field: 'requested_amount', operator: '>', value: '5000000000', label: 'amount > 5B' }
            ],
            defaultPath: 'rejected'
          },
          actions: []
        }
      },
      {
        id: 'ApprovalBM',
        type: 'creditNode',
        position: { x: 900, y: 80 },
        data: {
          nodeType: 'ApprovalNode',
          label: 'Approval Branch Manager',
          description: 'Persetujuan oleh Branch Manager',
          config: {
            approvalType: 'single',
            approvers: [{ role: 'Branch Manager' }],
            availableActions: ['approve', 'reject', 'return']
          },
          actions: []
        }
      },
      {
        id: 'ApprovalRM',
        type: 'creditNode',
        position: { x: 1040, y: 80 },
        data: {
          nodeType: 'ApprovalNode',
          label: 'Approval Regional Manager',
          description: 'Persetujuan oleh Regional Manager untuk kredit > 5 Miliar',
          config: {
            approvalType: 'single',
            approvers: [{ role: 'Regional Manager' }],
            availableActions: ['approve', 'reject', 'return']
          },
          actions: []
        }
      },
      {
        id: 'EndApproved',
        type: 'creditNode',
        position: { x: 1180, y: 60 },
        data: {
          nodeType: 'EndNode',
          label: 'Disetujui',
          description: 'Kredit disetujui',
          config: { outcome: 'approved', finalActions: [], notifications: [] },
          actions: []
        }
      },
      {
        id: 'EndRejected',
        type: 'creditNode',
        position: { x: 900, y: 250 },
        data: {
          nodeType: 'EndNode',
          label: 'Ditolak',
          description: 'Kredit ditolak',
          config: { outcome: 'rejected', finalActions: [], notifications: [] },
          actions: []
        }
      }
    ],
    edges: [
      {
        id: 'Flow_1',
        source: 'StartEvent_1',
        target: 'FormBorrower',
        sourceHandle: 'Flow_1',
        label: '',
        data: { label: '' }
      },
      {
        id: 'Flow_2',
        source: 'FormBorrower',
        target: 'FormFacility',
        sourceHandle: 'Flow_2',
        label: '',
        data: { label: '' }
      },
      {
        id: 'Flow_3',
        source: 'FormFacility',
        target: 'FormFinancial',
        sourceHandle: 'Flow_3',
        label: '',
        data: { label: '' }
      },
      {
        id: 'Flow_4',
        source: 'FormFinancial',
        target: 'SLAReview',
        sourceHandle: 'Flow_4',
        label: '',
        data: { label: '' }
      },
      {
        id: 'Flow_5',
        source: 'SLAReview',
        target: 'DecisionAmount',
        sourceHandle: 'Flow_5',
        label: '',
        data: { label: '' }
      },
      {
        id: 'Flow_6',
        source: 'DecisionAmount',
        target: 'ApprovalBM',
        sourceHandle: 'amount <= 5B',
        label: 'amount <= 5B',
        data: { label: 'amount <= 5B' }
      },
      {
        id: 'Flow_Reject1',
        source: 'DecisionAmount',
        target: 'EndRejected',
        sourceHandle: 'rejected',
        label: 'rejected',
        data: { label: 'rejected' }
      },
      {
        id: 'Flow_7',
        source: 'ApprovalBM',
        target: 'ApprovalRM',
        sourceHandle: 'amount > 5B',
        label: 'amount > 5B',
        data: { label: 'amount > 5B' }
      },
      {
        id: 'Flow_Reject2',
        source: 'ApprovalBM',
        target: 'EndRejected',
        sourceHandle: 'rejected',
        label: 'rejected',
        data: { label: 'rejected' }
      },
      {
        id: 'Flow_8',
        source: 'ApprovalRM',
        target: 'EndApproved',
        sourceHandle: 'approved',
        label: 'approved',
        data: { label: 'approved' }
      },
      {
        id: 'Flow_Reject3',
        source: 'ApprovalRM',
        target: 'EndRejected',
        sourceHandle: 'rejected',
        label: 'rejected',
        data: { label: 'rejected' }
      }
    ]
  },
  {
    id: 'collection_escalation',
    title: 'Eskalasi Penagihan',
    description: 'Alur penagihan bertingkat: assign collector, SLA timer, cek pembayaran, notifikasi supervisor, eskalasi delegasi, hingga write-off.',
    icon: 'LucideFileText',
    color: 'from-orange-500 to-red-500',
    xml: `<?xml version="1.0" encoding="UTF-8"?>
<bpmn:definitions xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"
                  xmlns:bpmn="http://www.omg.org/spec/BPMN/20100524/MODEL"
                  xmlns:bpmndi="http://www.omg.org/spec/BPMN/20100524/DI"
                  xmlns:dc="http://www.omg.org/spec/DD/20100524/DC"
                  xmlns:di="http://www.omg.org/spec/DD/20100524/DI"
                  id="Definitions_1"
                  targetNamespace="http://bpmn.io/schema/bpmn">
  <bpmn:process id="Process_1" isExecutable="true">
    <bpmn:startEvent id="StartEvent_1" name="Mulai">
      <bpmn:outgoing>Flow_1</bpmn:outgoing>
    </bpmn:startEvent>
    <bpmn:userTask id="AssignCollector" name="Assign Collector">
      <bpmn:incoming>Flow_1</bpmn:incoming>
      <bpmn:outgoing>Flow_2</bpmn:outgoing>
    </bpmn:userTask>
    <bpmn:serviceTask id="SLATimer1" name="SLA Timer 72 Jam">
      <bpmn:incoming>Flow_2</bpmn:incoming>
      <bpmn:outgoing>Flow_3</bpmn:outgoing>
    </bpmn:serviceTask>
    <bpmn:exclusiveGateway id="CekBayar1" name="Cek Pembayaran">
      <bpmn:incoming>Flow_3</bpmn:incoming>
      <bpmn:outgoing>Flow_4</bpmn:outgoing>
      <bpmn:outgoing>Flow_5</bpmn:outgoing>
    </bpmn:exclusiveGateway>
    <bpmn:endEvent id="EndLunas1" name="Lunas">
      <bpmn:incoming>Flow_4</bpmn:incoming>
    </bpmn:endEvent>
    <bpmn:serviceTask id="NotifSupervisor" name="Notifikasi Supervisor">
      <bpmn:incoming>Flow_5</bpmn:incoming>
      <bpmn:outgoing>Flow_6</bpmn:outgoing>
    </bpmn:serviceTask>
    <bpmn:userTask id="EskalasiDelegasi" name="Eskalasi Delegasi">
      <bpmn:incoming>Flow_6</bpmn:incoming>
      <bpmn:outgoing>Flow_7</bpmn:outgoing>
    </bpmn:userTask>
    <bpmn:serviceTask id="SLATimer2" name="SLA Timer 120 Jam">
      <bpmn:incoming>Flow_7</bpmn:incoming>
      <bpmn:outgoing>Flow_8</bpmn:outgoing>
    </bpmn:serviceTask>
    <bpmn:exclusiveGateway id="CekBayar2" name="Cek Pembayaran 2">
      <bpmn:incoming>Flow_8</bpmn:incoming>
      <bpmn:outgoing>Flow_9</bpmn:outgoing>
      <bpmn:outgoing>Flow_10</bpmn:outgoing>
    </bpmn:exclusiveGateway>
    <bpmn:endEvent id="EndLunas2" name="Lunas">
      <bpmn:incoming>Flow_9</bpmn:incoming>
    </bpmn:endEvent>
    <bpmn:endEvent id="EndWriteOff" name="Write-off">
      <bpmn:incoming>Flow_10</bpmn:incoming>
    </bpmn:endEvent>
    <bpmn:sequenceFlow id="Flow_1" sourceRef="StartEvent_1" targetRef="AssignCollector" />
    <bpmn:sequenceFlow id="Flow_2" sourceRef="AssignCollector" targetRef="SLATimer1" />
    <bpmn:sequenceFlow id="Flow_3" sourceRef="SLATimer1" targetRef="CekBayar1" />
    <bpmn:sequenceFlow id="Flow_4" name="paid" sourceRef="CekBayar1" targetRef="EndLunas1" />
    <bpmn:sequenceFlow id="Flow_5" name="not_paid" sourceRef="CekBayar1" targetRef="NotifSupervisor" />
    <bpmn:sequenceFlow id="Flow_6" sourceRef="NotifSupervisor" targetRef="EskalasiDelegasi" />
    <bpmn:sequenceFlow id="Flow_7" sourceRef="EskalasiDelegasi" targetRef="SLATimer2" />
    <bpmn:sequenceFlow id="Flow_8" sourceRef="SLATimer2" targetRef="CekBayar2" />
    <bpmn:sequenceFlow id="Flow_9" name="paid" sourceRef="CekBayar2" targetRef="EndLunas2" />
    <bpmn:sequenceFlow id="Flow_10" name="not_paid" sourceRef="CekBayar2" targetRef="EndWriteOff" />
  </bpmn:process>
  <bpmndi:BPMNDiagram id="BPMNDiagram_1">
    <bpmndi:BPMNPlane id="BPMNPlane_1" bpmnElement="Process_1">
      <bpmndi:BPMNShape id="_BPMNShape_StartEvent" bpmnElement="StartEvent_1">
        <dc:Bounds x="100" y="150" width="36" height="36" />
      </bpmndi:BPMNShape>
      <bpmndi:BPMNShape id="AssignCollector_di" bpmnElement="AssignCollector">
        <dc:Bounds x="200" y="128" width="100" height="80" />
      </bpmndi:BPMNShape>
      <bpmndi:BPMNShape id="SLATimer1_di" bpmnElement="SLATimer1">
        <dc:Bounds x="340" y="128" width="100" height="80" />
      </bpmndi:BPMNShape>
      <bpmndi:BPMNShape id="CekBayar1_di" bpmnElement="CekBayar1" isMarkerVisible="true">
        <dc:Bounds x="480" y="143" width="50" height="50" />
      </bpmndi:BPMNShape>
      <bpmndi:BPMNShape id="EndLunas1_di" bpmnElement="EndLunas1">
        <dc:Bounds x="580" y="80" width="36" height="36" />
      </bpmndi:BPMNShape>
      <bpmndi:BPMNShape id="NotifSupervisor_di" bpmnElement="NotifSupervisor">
        <dc:Bounds x="580" y="200" width="100" height="80" />
      </bpmndi:BPMNShape>
      <bpmndi:BPMNShape id="EskalasiDelegasi_di" bpmnElement="EskalasiDelegasi">
        <dc:Bounds x="720" y="200" width="100" height="80" />
      </bpmndi:BPMNShape>
      <bpmndi:BPMNShape id="SLATimer2_di" bpmnElement="SLATimer2">
        <dc:Bounds x="860" y="200" width="100" height="80" />
      </bpmndi:BPMNShape>
      <bpmndi:BPMNShape id="CekBayar2_di" bpmnElement="CekBayar2" isMarkerVisible="true">
        <dc:Bounds x="1000" y="215" width="50" height="50" />
      </bpmndi:BPMNShape>
      <bpmndi:BPMNShape id="EndLunas2_di" bpmnElement="EndLunas2">
        <dc:Bounds x="1100" y="150" width="36" height="36" />
      </bpmndi:BPMNShape>
      <bpmndi:BPMNShape id="EndWriteOff_di" bpmnElement="EndWriteOff">
        <dc:Bounds x="1100" y="280" width="36" height="36" />
      </bpmndi:BPMNShape>
      <bpmndi:BPMNEdge id="Flow_1_di" bpmnElement="Flow_1">
        <di:waypoint x="136" y="168" />
        <di:waypoint x="200" y="168" />
      </bpmndi:BPMNEdge>
      <bpmndi:BPMNEdge id="Flow_2_di" bpmnElement="Flow_2">
        <di:waypoint x="300" y="168" />
        <di:waypoint x="340" y="168" />
      </bpmndi:BPMNEdge>
      <bpmndi:BPMNEdge id="Flow_3_di" bpmnElement="Flow_3">
        <di:waypoint x="440" y="168" />
        <di:waypoint x="480" y="168" />
      </bpmndi:BPMNEdge>
      <bpmndi:BPMNEdge id="Flow_4_di" bpmnElement="Flow_4">
        <di:waypoint x="505" y="143" />
        <di:waypoint x="580" y="98" />
      </bpmndi:BPMNEdge>
      <bpmndi:BPMNEdge id="Flow_5_di" bpmnElement="Flow_5">
        <di:waypoint x="505" y="193" />
        <di:waypoint x="580" y="240" />
      </bpmndi:BPMNEdge>
      <bpmndi:BPMNEdge id="Flow_6_di" bpmnElement="Flow_6">
        <di:waypoint x="680" y="240" />
        <di:waypoint x="720" y="240" />
      </bpmndi:BPMNEdge>
      <bpmndi:BPMNEdge id="Flow_7_di" bpmnElement="Flow_7">
        <di:waypoint x="820" y="240" />
        <di:waypoint x="860" y="240" />
      </bpmndi:BPMNEdge>
      <bpmndi:BPMNEdge id="Flow_8_di" bpmnElement="Flow_8">
        <di:waypoint x="960" y="240" />
        <di:waypoint x="1000" y="240" />
      </bpmndi:BPMNEdge>
      <bpmndi:BPMNEdge id="Flow_9_di" bpmnElement="Flow_9">
        <di:waypoint x="1025" y="215" />
        <di:waypoint x="1100" y="168" />
      </bpmndi:BPMNEdge>
      <bpmndi:BPMNEdge id="Flow_10_di" bpmnElement="Flow_10">
        <di:waypoint x="1025" y="265" />
        <di:waypoint x="1100" y="298" />
      </bpmndi:BPMNEdge>
    </bpmndi:BPMNPlane>
  </bpmndi:BPMNDiagram>
</bpmn:definitions>`,
    elementConfigs: {
      StartEvent_1: {
        nodeType: 'StartNode',
        label: 'Mulai',
        description: 'Titik awal proses penagihan',
        config: { triggerType: 'manual', applicableProducts: [], applicablePersonas: [] },
        actions: []
      },
      AssignCollector: {
        nodeType: 'AssignmentNode',
        label: 'Assign Collector',
        description: 'Penugasan collector untuk menagih',
        config: {
          assignmentType: 'role_based',
          targetRole: 'Collector',
          availableActions: ['assign', 'reassign']
        },
        actions: []
      },
      SLATimer1: {
        nodeType: 'SLANode',
        label: 'SLA Timer 72 Jam',
        description: 'Batas waktu penagihan tahap 1',
        config: {
          deadlineHours: 72,
          warningHours: 48,
          reminderIntervalHours: 12,
          escalationTarget: 'Supervisor Collection',
          escalationAction: 'notify',
          businessHoursOnly: false
        },
        actions: []
      },
      CekBayar1: {
        nodeType: 'DecisionNode',
        label: 'Cek Pembayaran',
        description: 'Apakah debitur sudah membayar?',
        config: {
          conditions: [
            { id: 'cond_paid', field: 'payment_status', operator: '==', value: 'paid', label: 'paid' },
            { id: 'cond_not_paid', field: 'payment_status', operator: '!=', value: 'paid', label: 'not_paid' }
          ],
          defaultPath: 'not_paid'
        },
        actions: []
      },
      EndLunas1: {
        nodeType: 'EndNode',
        label: 'Lunas',
        description: 'Pembayaran lunas tahap 1',
        config: { outcome: 'paid', finalActions: [], notifications: [] },
        actions: []
      },
      NotifSupervisor: {
        nodeType: 'NotificationNode',
        label: 'Notifikasi Supervisor',
        description: 'Kirim notifikasi ke supervisor bahwa debitur belum membayar',
        config: {
          notificationType: 'email',
          recipients: [{ role: 'Supervisor Collection' }],
          template: 'collection_escalation_notify',
          message: 'Debitur belum melakukan pembayaran setelah batas waktu tahap 1.'
        },
        actions: []
      },
      EskalasiDelegasi: {
        nodeType: 'DelegationNode',
        label: 'Eskalasi Delegasi',
        description: 'Delegasi penagihan ke tim eskalasi',
        config: {
          delegationType: 'escalation',
          targetRole: 'Senior Collector',
          availableActions: ['delegate', 'reassign']
        },
        actions: []
      },
      SLATimer2: {
        nodeType: 'SLANode',
        label: 'SLA Timer 120 Jam',
        description: 'Batas waktu penagihan tahap 2',
        config: {
          deadlineHours: 120,
          warningHours: 96,
          reminderIntervalHours: 24,
          escalationTarget: 'Manager Collection',
          escalationAction: 'escalate',
          businessHoursOnly: false
        },
        actions: []
      },
      CekBayar2: {
        nodeType: 'DecisionNode',
        label: 'Cek Pembayaran 2',
        description: 'Apakah debitur sudah membayar setelah eskalasi?',
        config: {
          conditions: [
            { id: 'cond_paid2', field: 'payment_status', operator: '==', value: 'paid', label: 'paid' },
            { id: 'cond_not_paid2', field: 'payment_status', operator: '!=', value: 'paid', label: 'not_paid' }
          ],
          defaultPath: 'not_paid'
        },
        actions: []
      },
      EndLunas2: {
        nodeType: 'EndNode',
        label: 'Lunas',
        description: 'Pembayaran lunas tahap 2',
        config: { outcome: 'paid', finalActions: [], notifications: [] },
        actions: []
      },
      EndWriteOff: {
        nodeType: 'EndNode',
        label: 'Write-off',
        description: 'Kredit dihapusbukukan',
        config: { outcome: 'write_off', finalActions: [], notifications: [] },
        actions: []
      }
    },
    nodes: [
      {
        id: 'StartEvent_1',
        type: 'creditNode',
        position: { x: 100, y: 150 },
        data: {
          nodeType: 'StartNode',
          label: 'Mulai',
          description: 'Titik awal proses penagihan',
          config: { triggerType: 'manual', applicableProducts: [], applicablePersonas: [] },
          actions: []
        }
      },
      {
        id: 'AssignCollector',
        type: 'creditNode',
        position: { x: 200, y: 128 },
        data: {
          nodeType: 'AssignmentNode',
          label: 'Assign Collector',
          description: 'Penugasan collector untuk menagih',
          config: {
            assignmentType: 'role_based',
            targetRole: 'Collector',
            availableActions: ['assign', 'reassign']
          },
          actions: []
        }
      },
      {
        id: 'SLATimer1',
        type: 'creditNode',
        position: { x: 340, y: 128 },
        data: {
          nodeType: 'SLANode',
          label: 'SLA Timer 72 Jam',
          description: 'Batas waktu penagihan tahap 1',
          config: {
            deadlineHours: 72,
            warningHours: 48,
            reminderIntervalHours: 12,
            escalationTarget: 'Supervisor Collection',
            escalationAction: 'notify',
            businessHoursOnly: false
          },
          actions: []
        }
      },
      {
        id: 'CekBayar1',
        type: 'creditNode',
        position: { x: 480, y: 143 },
        data: {
          nodeType: 'DecisionNode',
          label: 'Cek Pembayaran',
          description: 'Apakah debitur sudah membayar?',
          config: {
            conditions: [
              { id: 'cond_paid', field: 'payment_status', operator: '==', value: 'paid', label: 'paid' },
              { id: 'cond_not_paid', field: 'payment_status', operator: '!=', value: 'paid', label: 'not_paid' }
            ],
            defaultPath: 'not_paid'
          },
          actions: []
        }
      },
      {
        id: 'EndLunas1',
        type: 'creditNode',
        position: { x: 580, y: 80 },
        data: {
          nodeType: 'EndNode',
          label: 'Lunas',
          description: 'Pembayaran lunas tahap 1',
          config: { outcome: 'paid', finalActions: [], notifications: [] },
          actions: []
        }
      },
      {
        id: 'NotifSupervisor',
        type: 'creditNode',
        position: { x: 580, y: 200 },
        data: {
          nodeType: 'NotificationNode',
          label: 'Notifikasi Supervisor',
          description: 'Kirim notifikasi ke supervisor bahwa debitur belum membayar',
          config: {
            notificationType: 'email',
            recipients: [{ role: 'Supervisor Collection' }],
            template: 'collection_escalation_notify',
            message: 'Debitur belum melakukan pembayaran setelah batas waktu tahap 1.'
          },
          actions: []
        }
      },
      {
        id: 'EskalasiDelegasi',
        type: 'creditNode',
        position: { x: 720, y: 200 },
        data: {
          nodeType: 'DelegationNode',
          label: 'Eskalasi Delegasi',
          description: 'Delegasi penagihan ke tim eskalasi',
          config: {
            delegationType: 'escalation',
            targetRole: 'Senior Collector',
            availableActions: ['delegate', 'reassign']
          },
          actions: []
        }
      },
      {
        id: 'SLATimer2',
        type: 'creditNode',
        position: { x: 860, y: 200 },
        data: {
          nodeType: 'SLANode',
          label: 'SLA Timer 120 Jam',
          description: 'Batas waktu penagihan tahap 2',
          config: {
            deadlineHours: 120,
            warningHours: 96,
            reminderIntervalHours: 24,
            escalationTarget: 'Manager Collection',
            escalationAction: 'escalate',
            businessHoursOnly: false
          },
          actions: []
        }
      },
      {
        id: 'CekBayar2',
        type: 'creditNode',
        position: { x: 1000, y: 215 },
        data: {
          nodeType: 'DecisionNode',
          label: 'Cek Pembayaran 2',
          description: 'Apakah debitur sudah membayar setelah eskalasi?',
          config: {
            conditions: [
              { id: 'cond_paid2', field: 'payment_status', operator: '==', value: 'paid', label: 'paid' },
              { id: 'cond_not_paid2', field: 'payment_status', operator: '!=', value: 'paid', label: 'not_paid' }
            ],
            defaultPath: 'not_paid'
          },
          actions: []
        }
      },
      {
        id: 'EndLunas2',
        type: 'creditNode',
        position: { x: 1100, y: 150 },
        data: {
          nodeType: 'EndNode',
          label: 'Lunas',
          description: 'Pembayaran lunas tahap 2',
          config: { outcome: 'paid', finalActions: [], notifications: [] },
          actions: []
        }
      },
      {
        id: 'EndWriteOff',
        type: 'creditNode',
        position: { x: 1100, y: 280 },
        data: {
          nodeType: 'EndNode',
          label: 'Write-off',
          description: 'Kredit dihapusbukukan',
          config: { outcome: 'write_off', finalActions: [], notifications: [] },
          actions: []
        }
      }
    ],
    edges: [
      {
        id: 'Flow_1',
        source: 'StartEvent_1',
        target: 'AssignCollector',
        sourceHandle: 'Flow_1',
        label: '',
        data: { label: '' }
      },
      {
        id: 'Flow_2',
        source: 'AssignCollector',
        target: 'SLATimer1',
        sourceHandle: 'Flow_2',
        label: '',
        data: { label: '' }
      },
      {
        id: 'Flow_3',
        source: 'SLATimer1',
        target: 'CekBayar1',
        sourceHandle: 'Flow_3',
        label: '',
        data: { label: '' }
      },
      {
        id: 'Flow_4',
        source: 'CekBayar1',
        target: 'EndLunas1',
        sourceHandle: 'paid',
        label: 'paid',
        data: { label: 'paid' }
      },
      {
        id: 'Flow_5',
        source: 'CekBayar1',
        target: 'NotifSupervisor',
        sourceHandle: 'not_paid',
        label: 'not_paid',
        data: { label: 'not_paid' }
      },
      {
        id: 'Flow_6',
        source: 'NotifSupervisor',
        target: 'EskalasiDelegasi',
        sourceHandle: 'Flow_6',
        label: '',
        data: { label: '' }
      },
      {
        id: 'Flow_7',
        source: 'EskalasiDelegasi',
        target: 'SLATimer2',
        sourceHandle: 'Flow_7',
        label: '',
        data: { label: '' }
      },
      {
        id: 'Flow_8',
        source: 'SLATimer2',
        target: 'CekBayar2',
        sourceHandle: 'Flow_8',
        label: '',
        data: { label: '' }
      },
      {
        id: 'Flow_9',
        source: 'CekBayar2',
        target: 'EndLunas2',
        sourceHandle: 'paid',
        label: 'paid',
        data: { label: 'paid' }
      },
      {
        id: 'Flow_10',
        source: 'CekBayar2',
        target: 'EndWriteOff',
        sourceHandle: 'not_paid',
        label: 'not_paid',
        data: { label: 'not_paid' }
      }
    ]
  },
  {
    id: 'kyc_verification',
    title: 'Verifikasi KYC',
    description: 'Alur verifikasi KYC: upload dokumen, verifikasi ID via API, AML screening, review manual jika diperlukan.',
    icon: 'LucideUserCheck',
    color: 'from-indigo-500 to-blue-600',
    xml: `<?xml version="1.0" encoding="UTF-8"?>
<bpmn:definitions xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"
                  xmlns:bpmn="http://www.omg.org/spec/BPMN/20100524/MODEL"
                  xmlns:bpmndi="http://www.omg.org/spec/BPMN/20100524/DI"
                  xmlns:dc="http://www.omg.org/spec/DD/20100524/DC"
                  xmlns:di="http://www.omg.org/spec/DD/20100524/DI"
                  id="Definitions_1"
                  targetNamespace="http://bpmn.io/schema/bpmn">
  <bpmn:process id="Process_1" isExecutable="true">
    <bpmn:startEvent id="StartEvent_1" name="Mulai">
      <bpmn:outgoing>Flow_1</bpmn:outgoing>
    </bpmn:startEvent>
    <bpmn:userTask id="UploadDokumen" name="Upload Dokumen">
      <bpmn:incoming>Flow_1</bpmn:incoming>
      <bpmn:outgoing>Flow_2</bpmn:outgoing>
    </bpmn:userTask>
    <bpmn:serviceTask id="VerifikasiIDAPI" name="Verifikasi ID API">
      <bpmn:incoming>Flow_2</bpmn:incoming>
      <bpmn:outgoing>Flow_3</bpmn:outgoing>
    </bpmn:serviceTask>
    <bpmn:exclusiveGateway id="CekVerified" name="Cek Verified">
      <bpmn:incoming>Flow_3</bpmn:incoming>
      <bpmn:outgoing>Flow_4</bpmn:outgoing>
      <bpmn:outgoing>Flow_Gagal</bpmn:outgoing>
    </bpmn:exclusiveGateway>
    <bpmn:serviceTask id="AMLScreening" name="AML Screening API">
      <bpmn:incoming>Flow_4</bpmn:incoming>
      <bpmn:outgoing>Flow_5</bpmn:outgoing>
    </bpmn:serviceTask>
    <bpmn:exclusiveGateway id="CekAML" name="Cek Lolos AML">
      <bpmn:incoming>Flow_5</bpmn:incoming>
      <bpmn:outgoing>Flow_6</bpmn:outgoing>
      <bpmn:outgoing>Flow_7</bpmn:outgoing>
    </bpmn:exclusiveGateway>
    <bpmn:endEvent id="EndVerified" name="Verified">
      <bpmn:incoming>Flow_6</bpmn:incoming>
    </bpmn:endEvent>
    <bpmn:userTask id="ReviewManual" name="Review Manual">
      <bpmn:incoming>Flow_7</bpmn:incoming>
      <bpmn:outgoing>Flow_8</bpmn:outgoing>
      <bpmn:outgoing>Flow_9</bpmn:outgoing>
    </bpmn:userTask>
    <bpmn:endEvent id="EndApprovedManual" name="Approved Manual">
      <bpmn:incoming>Flow_8</bpmn:incoming>
    </bpmn:endEvent>
    <bpmn:endEvent id="EndRejectedManual" name="Rejected Manual">
      <bpmn:incoming>Flow_9</bpmn:incoming>
    </bpmn:endEvent>
    <bpmn:endEvent id="EndGagalVerifikasi" name="Gagal Verifikasi">
      <bpmn:incoming>Flow_Gagal</bpmn:incoming>
    </bpmn:endEvent>
    <bpmn:sequenceFlow id="Flow_1" sourceRef="StartEvent_1" targetRef="UploadDokumen" />
    <bpmn:sequenceFlow id="Flow_2" sourceRef="UploadDokumen" targetRef="VerifikasiIDAPI" />
    <bpmn:sequenceFlow id="Flow_3" sourceRef="VerifikasiIDAPI" targetRef="CekVerified" />
    <bpmn:sequenceFlow id="Flow_4" name="verified" sourceRef="CekVerified" targetRef="AMLScreening" />
    <bpmn:sequenceFlow id="Flow_Gagal" name="not_verified" sourceRef="CekVerified" targetRef="EndGagalVerifikasi" />
    <bpmn:sequenceFlow id="Flow_5" sourceRef="AMLScreening" targetRef="CekAML" />
    <bpmn:sequenceFlow id="Flow_6" name="passed" sourceRef="CekAML" targetRef="EndVerified" />
    <bpmn:sequenceFlow id="Flow_7" name="flagged" sourceRef="CekAML" targetRef="ReviewManual" />
    <bpmn:sequenceFlow id="Flow_8" name="approved" sourceRef="ReviewManual" targetRef="EndApprovedManual" />
    <bpmn:sequenceFlow id="Flow_9" name="rejected" sourceRef="ReviewManual" targetRef="EndRejectedManual" />
  </bpmn:process>
  <bpmndi:BPMNDiagram id="BPMNDiagram_1">
    <bpmndi:BPMNPlane id="BPMNPlane_1" bpmnElement="Process_1">
      <bpmndi:BPMNShape id="_BPMNShape_StartEvent" bpmnElement="StartEvent_1">
        <dc:Bounds x="100" y="150" width="36" height="36" />
      </bpmndi:BPMNShape>
      <bpmndi:BPMNShape id="UploadDokumen_di" bpmnElement="UploadDokumen">
        <dc:Bounds x="200" y="128" width="100" height="80" />
      </bpmndi:BPMNShape>
      <bpmndi:BPMNShape id="VerifikasiIDAPI_di" bpmnElement="VerifikasiIDAPI">
        <dc:Bounds x="340" y="128" width="100" height="80" />
      </bpmndi:BPMNShape>
      <bpmndi:BPMNShape id="CekVerified_di" bpmnElement="CekVerified" isMarkerVisible="true">
        <dc:Bounds x="480" y="143" width="50" height="50" />
      </bpmndi:BPMNShape>
      <bpmndi:BPMNShape id="AMLScreening_di" bpmnElement="AMLScreening">
        <dc:Bounds x="580" y="80" width="100" height="80" />
      </bpmndi:BPMNShape>
      <bpmndi:BPMNShape id="CekAML_di" bpmnElement="CekAML" isMarkerVisible="true">
        <dc:Bounds x="720" y="95" width="50" height="50" />
      </bpmndi:BPMNShape>
      <bpmndi:BPMNShape id="EndVerified_di" bpmnElement="EndVerified">
        <dc:Bounds x="820" y="50" width="36" height="36" />
      </bpmndi:BPMNShape>
      <bpmndi:BPMNShape id="ReviewManual_di" bpmnElement="ReviewManual">
        <dc:Bounds x="820" y="150" width="100" height="80" />
      </bpmndi:BPMNShape>
      <bpmndi:BPMNShape id="EndApprovedManual_di" bpmnElement="EndApprovedManual">
        <dc:Bounds x="970" y="130" width="36" height="36" />
      </bpmndi:BPMNShape>
      <bpmndi:BPMNShape id="EndRejectedManual_di" bpmnElement="EndRejectedManual">
        <dc:Bounds x="970" y="220" width="36" height="36" />
      </bpmndi:BPMNShape>
      <bpmndi:BPMNShape id="EndGagalVerifikasi_di" bpmnElement="EndGagalVerifikasi">
        <dc:Bounds x="580" y="260" width="36" height="36" />
      </bpmndi:BPMNShape>
      <bpmndi:BPMNEdge id="Flow_1_di" bpmnElement="Flow_1">
        <di:waypoint x="136" y="168" />
        <di:waypoint x="200" y="168" />
      </bpmndi:BPMNEdge>
      <bpmndi:BPMNEdge id="Flow_2_di" bpmnElement="Flow_2">
        <di:waypoint x="300" y="168" />
        <di:waypoint x="340" y="168" />
      </bpmndi:BPMNEdge>
      <bpmndi:BPMNEdge id="Flow_3_di" bpmnElement="Flow_3">
        <di:waypoint x="440" y="168" />
        <di:waypoint x="480" y="168" />
      </bpmndi:BPMNEdge>
      <bpmndi:BPMNEdge id="Flow_4_di" bpmnElement="Flow_4">
        <di:waypoint x="505" y="143" />
        <di:waypoint x="580" y="120" />
      </bpmndi:BPMNEdge>
      <bpmndi:BPMNEdge id="Flow_Gagal_di" bpmnElement="Flow_Gagal">
        <di:waypoint x="505" y="193" />
        <di:waypoint x="580" y="278" />
      </bpmndi:BPMNEdge>
      <bpmndi:BPMNEdge id="Flow_5_di" bpmnElement="Flow_5">
        <di:waypoint x="680" y="120" />
        <di:waypoint x="720" y="120" />
      </bpmndi:BPMNEdge>
      <bpmndi:BPMNEdge id="Flow_6_di" bpmnElement="Flow_6">
        <di:waypoint x="745" y="95" />
        <di:waypoint x="820" y="68" />
      </bpmndi:BPMNEdge>
      <bpmndi:BPMNEdge id="Flow_7_di" bpmnElement="Flow_7">
        <di:waypoint x="745" y="145" />
        <di:waypoint x="820" y="190" />
      </bpmndi:BPMNEdge>
      <bpmndi:BPMNEdge id="Flow_8_di" bpmnElement="Flow_8">
        <di:waypoint x="920" y="170" />
        <di:waypoint x="970" y="148" />
      </bpmndi:BPMNEdge>
      <bpmndi:BPMNEdge id="Flow_9_di" bpmnElement="Flow_9">
        <di:waypoint x="920" y="210" />
        <di:waypoint x="970" y="238" />
      </bpmndi:BPMNEdge>
    </bpmndi:BPMNPlane>
  </bpmndi:BPMNDiagram>
</bpmn:definitions>`,
    elementConfigs: {
      StartEvent_1: {
        nodeType: 'StartNode',
        label: 'Mulai',
        description: 'Titik awal verifikasi KYC',
        config: { triggerType: 'manual', applicableProducts: [], applicablePersonas: [] },
        actions: []
      },
      UploadDokumen: {
        nodeType: 'DocumentNode',
        label: 'Upload Dokumen',
        description: 'Upload dokumen identitas nasabah',
        config: {
          documentTypes: ['KTP', 'Paspor', 'SIM'],
          maxFileSize: '10MB',
          requiredDocuments: ['KTP'],
          availableActions: ['upload', 'submit']
        },
        actions: []
      },
      VerifikasiIDAPI: {
        nodeType: 'IntegrationNode',
        label: 'Verifikasi ID API',
        description: 'Panggil API pihak ketiga untuk verifikasi identitas',
        config: {
          integrationId: 'id_verification_api',
          method: 'POST',
          endpoint: '/api/v1/verify-identity',
          timeout: 30,
          retryCount: 3
        },
        actions: []
      },
      CekVerified: {
        nodeType: 'DecisionNode',
        label: 'Cek Verified',
        description: 'Apakah identitas terverifikasi?',
        config: {
          conditions: [
            { id: 'cond_verified', field: 'id_verification_status', operator: '==', value: 'verified', label: 'verified' },
            { id: 'cond_not_verified', field: 'id_verification_status', operator: '!=', value: 'verified', label: 'not_verified' }
          ],
          defaultPath: 'not_verified'
        },
        actions: []
      },
      AMLScreening: {
        nodeType: 'IntegrationNode',
        label: 'AML Screening API',
        description: 'Panggil API AML/CFT screening',
        config: {
          integrationId: 'aml_screening_api',
          method: 'POST',
          endpoint: '/api/v1/aml-screening',
          timeout: 60,
          retryCount: 2
        },
        actions: []
      },
      CekAML: {
        nodeType: 'DecisionNode',
        label: 'Cek Lolos AML',
        description: 'Apakah nasabah lolos AML screening?',
        config: {
          conditions: [
            { id: 'cond_passed', field: 'aml_status', operator: '==', value: 'passed', label: 'passed' },
            { id: 'cond_flagged', field: 'aml_status', operator: '==', value: 'flagged', label: 'flagged' }
          ],
          defaultPath: 'flagged'
        },
        actions: []
      },
      EndVerified: {
        nodeType: 'EndNode',
        label: 'Verified',
        description: 'KYC berhasil diverifikasi',
        config: { outcome: 'verified', finalActions: [], notifications: [] },
        actions: []
      },
      ReviewManual: {
        nodeType: 'ApprovalNode',
        label: 'Review Manual',
        description: 'Review manual oleh Compliance Officer',
        config: {
          approvalType: 'single',
          approvers: [{ role: 'Compliance Officer' }],
          availableActions: ['approve', 'reject', 'return']
        },
        actions: []
      },
      EndApprovedManual: {
        nodeType: 'EndNode',
        label: 'Approved Manual',
        description: 'KYC disetujui setelah review manual',
        config: { outcome: 'approved', finalActions: [], notifications: [] },
        actions: []
      },
      EndRejectedManual: {
        nodeType: 'EndNode',
        label: 'Rejected Manual',
        description: 'KYC ditolak setelah review manual',
        config: { outcome: 'rejected', finalActions: [], notifications: [] },
        actions: []
      },
      EndGagalVerifikasi: {
        nodeType: 'EndNode',
        label: 'Gagal Verifikasi',
        description: 'Verifikasi identitas gagal',
        config: { outcome: 'failed', finalActions: [], notifications: [] },
        actions: []
      }
    },
    nodes: [
      {
        id: 'StartEvent_1',
        type: 'creditNode',
        position: { x: 100, y: 150 },
        data: {
          nodeType: 'StartNode',
          label: 'Mulai',
          description: 'Titik awal verifikasi KYC',
          config: { triggerType: 'manual', applicableProducts: [], applicablePersonas: [] },
          actions: []
        }
      },
      {
        id: 'UploadDokumen',
        type: 'creditNode',
        position: { x: 200, y: 128 },
        data: {
          nodeType: 'DocumentNode',
          label: 'Upload Dokumen',
          description: 'Upload dokumen identitas nasabah',
          config: {
            documentTypes: ['KTP', 'Paspor', 'SIM'],
            maxFileSize: '10MB',
            requiredDocuments: ['KTP'],
            availableActions: ['upload', 'submit']
          },
          actions: []
        }
      },
      {
        id: 'VerifikasiIDAPI',
        type: 'creditNode',
        position: { x: 340, y: 128 },
        data: {
          nodeType: 'IntegrationNode',
          label: 'Verifikasi ID API',
          description: 'Panggil API pihak ketiga untuk verifikasi identitas',
          config: {
            integrationId: 'id_verification_api',
            method: 'POST',
            endpoint: '/api/v1/verify-identity',
            timeout: 30,
            retryCount: 3
          },
          actions: []
        }
      },
      {
        id: 'CekVerified',
        type: 'creditNode',
        position: { x: 480, y: 143 },
        data: {
          nodeType: 'DecisionNode',
          label: 'Cek Verified',
          description: 'Apakah identitas terverifikasi?',
          config: {
            conditions: [
              { id: 'cond_verified', field: 'id_verification_status', operator: '==', value: 'verified', label: 'verified' },
              { id: 'cond_not_verified', field: 'id_verification_status', operator: '!=', value: 'verified', label: 'not_verified' }
            ],
            defaultPath: 'not_verified'
          },
          actions: []
        }
      },
      {
        id: 'AMLScreening',
        type: 'creditNode',
        position: { x: 580, y: 80 },
        data: {
          nodeType: 'IntegrationNode',
          label: 'AML Screening API',
          description: 'Panggil API AML/CFT screening',
          config: {
            integrationId: 'aml_screening_api',
            method: 'POST',
            endpoint: '/api/v1/aml-screening',
            timeout: 60,
            retryCount: 2
          },
          actions: []
        }
      },
      {
        id: 'CekAML',
        type: 'creditNode',
        position: { x: 720, y: 95 },
        data: {
          nodeType: 'DecisionNode',
          label: 'Cek Lolos AML',
          description: 'Apakah nasabah lolos AML screening?',
          config: {
            conditions: [
              { id: 'cond_passed', field: 'aml_status', operator: '==', value: 'passed', label: 'passed' },
              { id: 'cond_flagged', field: 'aml_status', operator: '==', value: 'flagged', label: 'flagged' }
            ],
            defaultPath: 'flagged'
          },
          actions: []
        }
      },
      {
        id: 'EndVerified',
        type: 'creditNode',
        position: { x: 820, y: 50 },
        data: {
          nodeType: 'EndNode',
          label: 'Verified',
          description: 'KYC berhasil diverifikasi',
          config: { outcome: 'verified', finalActions: [], notifications: [] },
          actions: []
        }
      },
      {
        id: 'ReviewManual',
        type: 'creditNode',
        position: { x: 820, y: 150 },
        data: {
          nodeType: 'ApprovalNode',
          label: 'Review Manual',
          description: 'Review manual oleh Compliance Officer',
          config: {
            approvalType: 'single',
            approvers: [{ role: 'Compliance Officer' }],
            availableActions: ['approve', 'reject', 'return']
          },
          actions: []
        }
      },
      {
        id: 'EndApprovedManual',
        type: 'creditNode',
        position: { x: 970, y: 130 },
        data: {
          nodeType: 'EndNode',
          label: 'Approved Manual',
          description: 'KYC disetujui setelah review manual',
          config: { outcome: 'approved', finalActions: [], notifications: [] },
          actions: []
        }
      },
      {
        id: 'EndRejectedManual',
        type: 'creditNode',
        position: { x: 970, y: 220 },
        data: {
          nodeType: 'EndNode',
          label: 'Rejected Manual',
          description: 'KYC ditolak setelah review manual',
          config: { outcome: 'rejected', finalActions: [], notifications: [] },
          actions: []
        }
      },
      {
        id: 'EndGagalVerifikasi',
        type: 'creditNode',
        position: { x: 580, y: 260 },
        data: {
          nodeType: 'EndNode',
          label: 'Gagal Verifikasi',
          description: 'Verifikasi identitas gagal',
          config: { outcome: 'failed', finalActions: [], notifications: [] },
          actions: []
        }
      }
    ],
    edges: [
      {
        id: 'Flow_1',
        source: 'StartEvent_1',
        target: 'UploadDokumen',
        sourceHandle: 'Flow_1',
        label: '',
        data: { label: '' }
      },
      {
        id: 'Flow_2',
        source: 'UploadDokumen',
        target: 'VerifikasiIDAPI',
        sourceHandle: 'Flow_2',
        label: '',
        data: { label: '' }
      },
      {
        id: 'Flow_3',
        source: 'VerifikasiIDAPI',
        target: 'CekVerified',
        sourceHandle: 'Flow_3',
        label: '',
        data: { label: '' }
      },
      {
        id: 'Flow_4',
        source: 'CekVerified',
        target: 'AMLScreening',
        sourceHandle: 'verified',
        label: 'verified',
        data: { label: 'verified' }
      },
      {
        id: 'Flow_Gagal',
        source: 'CekVerified',
        target: 'EndGagalVerifikasi',
        sourceHandle: 'not_verified',
        label: 'not_verified',
        data: { label: 'not_verified' }
      },
      {
        id: 'Flow_5',
        source: 'AMLScreening',
        target: 'CekAML',
        sourceHandle: 'Flow_5',
        label: '',
        data: { label: '' }
      },
      {
        id: 'Flow_6',
        source: 'CekAML',
        target: 'EndVerified',
        sourceHandle: 'passed',
        label: 'passed',
        data: { label: 'passed' }
      },
      {
        id: 'Flow_7',
        source: 'CekAML',
        target: 'ReviewManual',
        sourceHandle: 'flagged',
        label: 'flagged',
        data: { label: 'flagged' }
      },
      {
        id: 'Flow_8',
        source: 'ReviewManual',
        target: 'EndApprovedManual',
        sourceHandle: 'approved',
        label: 'approved',
        data: { label: 'approved' }
      },
      {
        id: 'Flow_9',
        source: 'ReviewManual',
        target: 'EndRejectedManual',
        sourceHandle: 'rejected',
        label: 'rejected',
        data: { label: 'rejected' }
      }
    ]
  }
];
