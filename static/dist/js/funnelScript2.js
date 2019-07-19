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
    ["Reached Out", stage2, "#FFFFFF"],
    ["New Applicant", stage3, "#DCDCDC"],
    ["Recruiter Screen", stage4, "#FFFFFF"],
    ["Phone Interview", stage5, "#DCDCDC"],
    ["Onsite Interview", stage6, "#FFFFFF"],
    ["Offer", stage7, "#DCDCDC"]
  ];
  const options = {
    chart: {
      width: 400,
      height: 400,
      bottomWidth: 1 / 3,
      bottomPinch: 0,
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
      fill: "black"
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
