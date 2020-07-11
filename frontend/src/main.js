import Vue from "vue";
import VueCookie from "vue-cookies";
import App from "./App.vue";
import router from "./router";
import axios from "axios";
import jwt from "jsonwebtoken";

Vue.config.productionTip = false;
Vue.prototype.$http = axios;
Vue.prototype.$jwt = jwt;
Vue.use(VueCookie);

new Vue({
    router,
    render: h => h(App),
}).$mount("#app");
