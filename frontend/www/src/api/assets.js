import { GET, POST, PUT, DELETE } from '@/utils/request'

// 资产录入
export const AssetEntry = (asset) => POST('/api/assets/entry', asset)
export const AssetUpdate = (asset) => POST('/api/assets/update', asset)
export const AssetAllocation = (asset) => POST('/api/assets/allocation', asset)
export const AssetReturn = (asset) => POST('/api/assets/return', asset)
export const AssetDisposal = (asset) => POST('/api/assets/disposal', asset)
export const AssetTransfer = (asset) => POST('/api/assets/transfer', asset)
export const GetAssetLogs = (assetId, range) => GET('/api/assets/logs/' + assetId, range)
export const GetUserAssetLogs = (username, range) => GET('/api/assets/logs/user/' + username, range)
export const SearchAssetLogs = (searchData) => POST('/api/assets/logs/search', searchData)
export const GetAssetById = (assetId) => GET('/api/assets/' + assetId)
export const GetAssetCategoryTree = (search) => GET('/api/assets/category/tree', search)
export const AddNewAssetCategory = (category) => POST('/api/assets/category', category)
export const UpdateAssetCategory = (category) => PUT('/api/assets/category', category)
export const DeleteAssetCategory = (categoryId) => DELETE('/api/assets/category/' + categoryId)
export const GetAssetLocationTree = (search) => GET('/api/assets/location/tree', search)
export const AddNewAssetLocation = (location) => POST('/api/assets/location', location)
export const UpdateAssetLocation = (location) => PUT('/api/assets/location', location)
export const DeleteAssetLocation = (locationId) => DELETE('/api/assets/location/' + locationId)
export const GetAssetDepartmentTree = (search) => GET('/api/assets/department/tree', search)
export const AddNewAssetDepartment = (department) => POST('/api/assets/department', department)
export const UpdateAssetDepartment = (department) => PUT('/api/assets/department', department)
export const DeleteAssetDepartment = (departmentId) => DELETE('/api/assets/department/' + departmentId)
export const BulkAssetImport = (assets) => POST('/api/assets/import', assets)
export const GetAssetExport = () => GET('/api/assets/export', {}, true)

// 盘点相关接口
export const GetInventoryBatches = (searchData) => POST('/api/assets/inventory/batches/search', searchData)
export const CreateInventoryBatch = (batch) => POST('/api/assets/inventory/batches', batch)
export const UpdateInventoryBatch = (batchId, batch) => PUT('/api/assets/inventory/batches/' + batchId, batch)
export const GetInventoryRecords = (searchData) => POST('/api/assets/inventory/records/search', searchData)
export const CreateInventoryRecord = (formData) => POST('/api/assets/inventory/records', formData, {
  headers: {
    'Content-Type': 'multipart/form-data'
  }
})
export const DeleteInventoryBatch = (batchId) => DELETE('/api/assets/inventory/batches/' + batchId)
export const GetInventoryBatchById = (batchId) => GET('/api/assets/inventory/batches/' + batchId)
export const GetBatchInventoryRecords = (batchId, page = 1, size = 20) => GET('/api/assets/inventory/batches/' + batchId + '/records', { page, size })
export const GetInventoryBatchSummary = (batchId) => GET('/api/assets/inventory/batches/' + batchId + '/summary')
export const GetAssetInventoryLogs = (assetId, params) => GET('/api/assets/inventory/log/' + assetId, params)
