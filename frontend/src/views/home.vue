<template>
<base-layout>
  <template v-slot:main>
    <div class="home">
      <ul>
        <li><a href="#">Create or Modify a Board</a></li>
        <li><a href="#">Start a New Game</a></li>
        <li><a href="#">Join a Game</a></li>
      </ul>
    </div>
  </template>
</base-layout>
</template>

<script>
import BaseLayout from "@/layouts/base.vue";

export default {
  name: "Home",
  components: {
    "base-layout": BaseLayout
  },
  data() {
    return {
    }
  }
}
</script>
