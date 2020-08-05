<template>
<div class="category">
<p>{{ name }}</p>
<ul>
  <li v-for="tile in tiles" v-bind:key="tile.id">
    <tile v-bind:tile="tile"></tile>
  </li>
</ul>
</div>
</template>

<script>
import Tile from "./tile.vue";

export default {
  name: "Category",
  components: {
    "tile": Tile
  },
  data() {
    return {
    }
  },
  computed: {
    name() { return this.category.name; },
    tiles() { return this.category.tiles; }
  },
  props: {
    category: Object
  }
}
</script>
