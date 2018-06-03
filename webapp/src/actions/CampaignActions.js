import Reflux from 'reflux'
import api from 'utilities/api'

const CampaignActions = Reflux.createActions({
  'fetchCampaigns': { children: ['completed', 'failed'], asyncResult: true }
})

CampaignActions.fetchCampaigns.listenAndPromise(() => {
  return api.campaign(null, null)
})

export default CampaignActions
