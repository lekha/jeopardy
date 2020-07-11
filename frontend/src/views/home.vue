<template>
<div class="home">
  <template v-if="user">
    <p>Welcome, {{ user.name }}</p>
    <p><a href="/user/logout">Log Out</a></p>
    <ul>
      <li><a href="#">Create or Modify a Board</a></li>
      <li><a href="#">Start a New Game</a></li>
      <li><a href="#">Join a Game</a></li>
    </ul>
  </template>
  <a v-else :href="'/user/login?next='+endpoint">Log In with Google</a>
</div>
</template>

<script>
export default {
  name: "Home",
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
        this.$router.replace({"name": next});
      }
    }
  },
  beforeMount() {
    this.redirectToNext();
    this.user = this.currentUser();
  }
}
</script>
