/**
 * bpmnParser.js
 *
 * Bridge utility that parses BPMN 2.0 XML to the linear nodes/edges structure
 * required by the BNI FCRM state transition execution engine.
 */

export const INITIAL_XML = `<?xml version="1.0" encoding="UTF-8"?>
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
</bpmn:definitions>`

/**
 * Parses BPMN 2.0 XML and generates list-formatted nodes and edges
 * @param {string} xmlString - Standard BPMN XML string
 * @param {Object} elementConfigs - Map of element IDs to custom credit flow property configurations
 * @returns {Object} { nodes: Array, edges: Array }
 */
export function parseBPMN(xmlString, elementConfigs = {}) {
  const parser = new DOMParser()
  const doc = parser.parseFromString(xmlString, 'text/xml')

  const nodes = []
  const edges = []

  if (!doc || doc.getElementsByTagName('parsererror').length > 0) {
    console.error('BPMN XML Parse error', doc ? doc.getElementsByTagName('parsererror')[0] : 'Unknown')
    return { nodes, edges }
  }

  // 1. Gather all BPMN elements
  const processElements = doc.getElementsByTagName('bpmn:process')
  if (!processElements.length) return { nodes, edges }

  const processNode = processElements[0]
  const children = processNode.childNodes

  for (let i = 0; i < children.length; i++) {
    const child = children[i]
    if (child.nodeType !== 1) continue // only element nodes

    const nodeName = child.nodeName
    const elementId = child.getAttribute('id')
    const elementName = child.getAttribute('name') || ''

    // Map standard BPMN to custom credit flow types
    let nodeType = ''
    if (nodeName === 'bpmn:startEvent') {
      nodeType = 'StartNode'
    } else if (nodeName === 'bpmn:endEvent') {
      nodeType = 'EndNode'
    } else if (nodeName === 'bpmn:userTask') {
      // UserTask can be FormNode, ApprovalNode, CommitteeNode, DelegationNode, or AssignmentNode.
      // We look it up from the configurations map by default.
      const savedConfig = elementConfigs[elementId]
      nodeType = savedConfig?.nodeType || 'FormNode'
    } else if (nodeName === 'bpmn:exclusiveGateway') {
      // Gateway can be DecisionNode or SkipNode
      const savedConfig = elementConfigs[elementId]
      nodeType = savedConfig?.nodeType || 'DecisionNode'
    } else if (nodeName === 'bpmn:sendTask') {
      nodeType = 'NotificationNode'
    } else if (nodeName === 'bpmn:serviceTask') {
      nodeType = 'IntegrationNode'
    } else if (nodeName === 'bpmn:boundaryEvent') {
      nodeType = 'SLANode'
    }

    if (nodeType) {
      // Find positioning/bounds if available in BPMNDiagram elements
      let position = { x: 200, y: 150 }
      const shapeDi = doc.querySelector(`[bpmnElement="${elementId}"] dc\\:Bounds, [bpmnElement="${elementId}"] Bounds`)
      if (shapeDi) {
        position.x = parseFloat(shapeDi.getAttribute('x') || 200)
        position.y = parseFloat(shapeDi.getAttribute('y') || 150)
      }

      const savedConfig = elementConfigs[elementId] || {}
      nodes.push({
        id: elementId,
        type: 'creditNode',
        position,
        data: {
          nodeType,
          label: elementName || savedConfig.label || elementId,
          description: savedConfig.description || '',
          config: savedConfig.config || {},
          actions: savedConfig.actions || []
        }
      })
    }

    // 2. Map sequence flows to edges
    if (nodeName === 'bpmn:sequenceFlow') {
      const source = child.getAttribute('sourceRef')
      const target = child.getAttribute('targetRef')
      
      // Determine label or handle
      const flowLabel = elementName || ''
      edges.push({
        id: elementId,
        source,
        target,
        sourceHandle: flowLabel || elementId,
        label: flowLabel,
        data: { label: flowLabel }
      })
    }
  }

  return { nodes, edges }
}
