<template>
<div class="board">
  <ul>
    <li v-for="category in categories" v-bind:key="category.id">
      <category v-bind:category="category"></category>
    </li>
  </ul>
</div>
</template>

<script>
import Category from "./category.vue";

export default {
  name: "Board",
  components: {
    "category": Category
  },
  data() {
    return {
    }
  },
  computed: {
    categories() { return this.board.categories; }
  },
  props: {
    board: Object
  }
}
</script>
