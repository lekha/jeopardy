import Vue from 'vue';
import Router from 'vue-router';
import Buzzer from '@/components/Buzzer.vue';

Vue.use(Router);

export default new Router({
    routes: [
        {
            path: '/',
            name: 'Buzzer',
            component: Buzzer
        }
    ]
});
