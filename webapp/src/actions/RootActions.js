import Reflux from 'reflux'
import api from 'utilities/api'

const RootActions = Reflux.createActions({
  'fetchAllMeta': { children: ['completed', 'failed'] }
})

// API CALLS
// ---------------------------------------------------------------------------
// RootActions.fetchAllMeta.listenAndPromise(() => api.get_all_meta(null, null, {'cache-control': 'no-cache'}))
RootActions.fetchAllMeta.listenAndPromise(() => api.get_all_meta(null, null))


export default RootActions
