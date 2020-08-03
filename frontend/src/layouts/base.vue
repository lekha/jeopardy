<template>
<div class="base-layout">
  <template v-if="user">
    <p>Welcome, {{ user.name }}</p>
    <p><a href="/user/logout">Log Out</a></p>
    <slot name="main" v-bind:user="user"></slot>
  </template>
  <a v-else :href="'/user/login?next='+endpoint">Log In with Google</a>
</div>
</template>

<script>
export default {
  name: "BaseLayout",
  data() {
    return {
      endpoint: this.$route.name,
      user: ""
    }
  },
  methods: {
    currentUser() {
      var publicKey = process.env.VUE_APP_PUBLIC_KEY;
      publicKey = publicKey.replace(/\\n/g, "\n");
      var encodedUser = this.$cookies.get("user");
      var user;
      try {
        user = this.$jwt.verify(encodedUser, publicKey);
      } catch(err) {
        user = "";
        console.log(err);
      }
      return user;
    },
    redirectToNext() {
      var next = this.$route.query.next;
      if (next) {
        const [ name, gameCode ] = next.split(".");
        this.$router.replace({
          "name": name,
          "params": { gameCode: gameCode }
        });
      }
    }
  },
  beforeMount() {
    this.redirectToNext();
    this.user = this.currentUser();
  }
}
</script>
