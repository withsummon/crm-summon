export const workflowTemplates = [
  {
    id: 'simplified_credit',
    title: 'Simplified Credit Application',
    description: 'Alur kerja kredit sederhana: input data pemohon, data fasilitas, data keuangan, dan approval manager.',
    icon: 'LucideFileText',
    color: 'from-purple-500 to-violet-600',
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
  }
];
