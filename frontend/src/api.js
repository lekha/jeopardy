import axios from "axios";

export const api = {
  createGame() {
    return axios.post("/api/v1/game")
    .then(response => {
      return response.data;
    });
  },
  getGame(gameCode) {
    return axios.get("/api/v1/game/" + gameCode)
    .then(response => {
      return response.data;
    });
  },
  startGame(gameCode) {
    return axios.post("/api/v1/start/" + gameCode)
    .then(response => {
      return response.data;
    });
  }
}
