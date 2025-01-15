// 一些通用的js
/**
 * 将树形数据扁平化为 { id: node } 的形式
 * @param {Array} nodes - 树形数据
 * @param {Object} props - 属性配置，例如：{ id: 'id', children: 'children' }
 * @returns {Map} - 返回一个 Map，key 是节点的 id，value 是节点本身
 */
function flattenTree(nodes, props = {}) {
  const {id = 'id', children = 'children'} = props
  const nodeMap = new Map()

  function flatten(nodes) {
    nodes.forEach(node => {
      nodeMap.set(node[id], node) // 将节点存入 Map
      if (node[children] && node[children].length > 0) {
        flatten(node[children]) // 递归处理子节点
      }
    })
  }

  flatten(nodes)
  return nodeMap
}

/**
 * 通过 id 查找节点
 * @param {Map} nodeMap - 扁平化的节点 Map
 * @param {number|string} targetId - 目标节点的 id
 * @returns {Object|null} - 返回找到的节点，如果未找到则返回 null
 */
export function findNodeById(nodeMap, targetId) {
  return nodeMap.get(targetId) || null
}


/**
 * 通过id生成对应的层级label,例如：根节点/子节点/孙节点
 * @param {Array} data - 传入的树形数据, 例如：[{id: 1, name: '根节点', children: [{id: 2, name: '子节点', children: [{id: 3, name: '孙节点'}]}]}]
 * @param {number} findId - 传入的唯一值
 * @param {Object} props - 传入的属性，例如：{id: 'id', children: 'children', label: 'label',parent_id: 'parent_id'}
 * @returns {string} - 返回层级label,例如：根节点/子节点/孙节点
 */
export function getHierarchyLabel(data, findId, props) {
  const defaultProps = {
    id: 'id',
    children: 'children',
    label: 'label',
    parent_id: 'parent_id'
  }
  const id = props && props.hasOwnProperty('id') ? props.id : defaultProps.id
  const children = props && props.hasOwnProperty('children') ? props.children : defaultProps.children
  const label = props && props.hasOwnProperty('label') ? props.label : defaultProps.label
  const parent_id = props && props.hasOwnProperty('parent_id') ? props.parent_id : defaultProps.parent_id

  let nodeMap = flattenTree(data, {id: 'id', children: 'children'})
  let hierarchyLabel = ''
  while (true) {
    let selectNode = findNodeById(nodeMap, findId)
    hierarchyLabel = hierarchyLabel ? selectNode[label] + '/' + hierarchyLabel : selectNode[label]
    if (selectNode[parent_id] === null) {
      hierarchyLabel = '/' + hierarchyLabel
      break
    }
    findId = selectNode[parent_id]
  }
  console.log(hierarchyLabel)
  return hierarchyLabel
}


/**
 * 给[{},{}]类型的数据递归增加自定义属性值，并返回新数组
 * @param {Array} data - 传入的树形数据, 例如：[{id: 1, name: '根节点', children: [{id: 2, name: '子节点', children: [{id: 3, name: '孙节点'}]}]}]
 * @param {string} customProperty - 传入的自定义属性名称, 例如：'isExpanded'
 * @param value - 自定义的值
 * @returns {Array} - 返回新数组
 */
export function addCustomProperty(data, customProperty, value) {
  return data.map(item => {
    item[customProperty] = value
    if (item.children) {
      item.children = addCustomProperty(item.children, customProperty, value)
    }
    return item
  })
}

/**
 * 给[{},{}]类型的数据递归查找某个属性，修改值，并返回新数组
 * @param {Array} data - 传入的树形数据, 例如：[{id: 1, name: '根节点', children: [{id: 2, name: '子节点', children: [{id: 3, name: '孙节点'}]}]}]
 * @param {string} customProperty - 传入的自定义属性名称, 例如：'isExpanded'
 * @param value - 自定义的值
 * @param newValue - 新的值
 * @returns {Array} - 返回新数组
 */
export function updateCustomProperty(data, customProperty, value, newValue) {
  return data.map(item => {
    if (item[customProperty] === value) {
      item[customProperty] = newValue
    }
    if (item.children) {
      item.children = updateCustomProperty(item.children, customProperty, value, newValue)
    }
    return item
  })
}