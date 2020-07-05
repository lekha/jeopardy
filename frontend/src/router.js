import Vue from "vue";
import Router from "vue-router";
import Buzzer from "@/components/buzzer.vue";
import Home from "@/components/home.vue";

Vue.use(Router);

export default new Router({
    mode: "history",
    routes: [
        {
            path: "/",
            name: "home",
            component: Home
        },
        {
            path: "/buzzer",
            name: "Buzzer",
            component: Buzzer
        }
    ]
});
