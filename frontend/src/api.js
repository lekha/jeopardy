import axios from "axios";

export const api = {
  getGame(gameCode) {
    return axios.get("/api/v1/game/" + gameCode)
    .then(response => {
      return response.data;
    });
  }
}
