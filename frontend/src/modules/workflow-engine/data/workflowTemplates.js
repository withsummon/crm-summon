export const workflowTemplates = [
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
