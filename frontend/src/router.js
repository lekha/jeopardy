import Vue from "vue";
import Router from "vue-router";
import Buzzer from "@/components/buzzer.vue";
import Home from "@/views/home.vue";
import Play from "@/views/play.vue";

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
      name: "buzzer",
      component: Buzzer
    },
    {
      path: "/play/:gameCode",
      name: "play",
      component: Play
    }
  ]
});
