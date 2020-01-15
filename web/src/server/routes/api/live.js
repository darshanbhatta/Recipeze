const router = require("express").Router();

router.get("/", (res, req) => {
    req.send({ connected: true });
})

module.exports = router;