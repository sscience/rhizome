import Reflux from 'reflux'
import api from 'data/api'

var PermissionStore = Reflux.createStore({
  init () {
    this.permissions = []

    this.permissionsPromise = api.user_permissions()
      .then(data => {
        this.permissions = data.objects.map(p => {
          return p.auth_code
        })
        this.trigger({
          permissions: this.permissions
        })
        return this.permissions
      })
  },

  getInitialState () {
    return {
      permissions: this.permissions
    }
  },

  // API
  userHasPermission (permissionString) {
    return this.permissions.indexOf(permissionString.toLowerCase()) > -1
  },

  getPermissionsPromise () {
    return this.permissionsPromise
  }
})

export default PermissionStore
