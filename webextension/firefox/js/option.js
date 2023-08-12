let storage = browser.storage.local;
storage.set({ apiIp: "192.168.178.74:2020" });

function updateApiIp() {
  storage.set({ apiIp: this.value });
  console.log("API IP set to: ", storage.get("apiIp"));
}

function setupIpInput() {
  let ipInput = document.getElementsByName("ip-input")[0];
  ipInput.addEventListener("input", updateApiIp);

  storage.get("apiIp").then((item) => {
    ipInput.value = item.apiIp;
  });
}

setupIpInput();
