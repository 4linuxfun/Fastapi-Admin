// 一些通用的js
/**
 * 根据id查找节点,并返回节点内容
 * @param nodes
 * @param id
 * @returns {*|null}
 */
export function findNodeById(nodes, id) {
  for (let node of nodes) {
    if (node.id === id) {
      return node
    }
    if (node.children) {
      let found = findNodeById(node.children, id)
      if (found) {
        return found
      }
    }
  }
  return null
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

  let selectNode = findNodeById(data, findId)
  let hierarchyLabel = selectNode[label]
  let parent = selectNode[parent_id]
  console.log(selectNode, parent)
  while (parent !== null) {
    let parentItem = findNodeById(data, selectNode[parent_id])
    hierarchyLabel = parentItem[label] + ' / ' + hierarchyLabel
    parent = parentItem[parent_id]
  }
  return hierarchyLabel
}