const express = require("express");
const app = express();

app.use(express.static("dist"));
app.use(require("./routes"));


app.listen(process.env.PORT || 8080, () => console.log(`Listening on port ${process.env.PORT || 8080}!`));
