function trigger(
  funnelDiv,
  stage1,
  stage2,
  stage3,
  stage4,
  stage5,
  stage6,
  stage7
) {
  const data = [
    ["New Lead", stage1, "#DCDCDC"],
    ["Reached Out", stage2, "#D3D3D3"],
    ["New Applicant", stage3, "#C0C0C0"],
    ["Recruiter Screen", stage4, "#A9A9A9"],
    ["Phone Interview", stage5, "#808080"],
    ["Onsite Interview", stage6, "#696969"],
    ["Offer", stage7, "#696969"]
  ];
  const options = {
    chart: {
      width: 400,
      height: 400,
      bottomWidth: 1 / 3,
      bottomPinch: 1,
      animate: true,
      curve: {
        enabled: false,
        height: 40
      }
    },
    block: {
      dynamicHeight: false
      // dynamicSlope: true
    },
    label: {
      enabled: true,
      format: "{f} - {l}",
      fontFamily: null,
      fontSize: "14px",
      fill: "#fff"
    },
    tooltip: {
      enabled: true,
      format: "{l}: {f}"
    }
  };

  let tem = "#" + funnelDiv;

  const chartVar = new D3Funnel(tem);
  console.log("chart", chartVar, options);
  chartVar.draw(data, options);
}
// myFunc("funnelVar1", 12, 13, 14, 15, 16, 17, 18);
// myFunc("funnelVar2", 12, 13, 14, 15, 16, 17, 18);
