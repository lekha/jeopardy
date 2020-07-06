<template>
<div class="home">
  <a :href="'/user/login?next='+endpoint">Log In with Google</a>
</div>
</template>

<script>
export default {
  name: "Home",
  data() {
    return {
      endpoint: this.$route.name
    }
  },
  methods: {
    redirectToNext() {
      var next = this.$route.query.next;
      if (next) {
        this.$router.replace({"name": next});
      }
    }
  },
  beforeMount() {
    this.redirectToNext();
  }
}
</script>
