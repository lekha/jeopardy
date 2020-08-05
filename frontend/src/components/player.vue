<template>
<p class="player">{{ username }}</p>
</template>

<script>
export default {
  name: "Player",
  data() {
    return {
    }
  },
  computed: {
    username() { return this.player.username; }
  },
  props: {
    player: Object
  }
}
</script>
