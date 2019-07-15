function trigger(
  triggerDiv,
  stage1,
  stage2,
  stage3,
  stage4,
  stage5,
  stage6,
  stage7
) {
  // Themes begin
  // Randomizing themes
  let allThemes = [
    am4themes_animated,
    am4themes_material,
    am4themes_dataviz,
    am4themes_kelly,
    am4themes_frozen,
    am4themes_moonrisekingdom,
    am4themes_spiritedaway
  ];
  let currentThemee = allThemes[Math.floor(Math.random() * allThemes.length)];
  am4core.useTheme(currentThemee);
  // Themes end

  let chart = am4core.create(`${triggerDiv}`, am4charts.SlicedChart);
  chart.data = [
    {
      name: "New Lead",
      value: `${stage1}`
    },
    {
      name: "Reached Out",
      value: `${stage2}`
    },
    {
      name: "New Applicant",
      value: `${stage3}`
    },
    {
      name: "Recruiter Screen",
      value: `${stage4}`
    },
    {
      name: "Phone Interview",
      value: `${stage5}`
    },
    {
      name: "Onsite Interview",
      value: `${stage6}`
    },
    {
      name: "Offer",
      value: `${stage7}`
    }
  ];

  let series = chart.series.push(new am4charts.FunnelSeries());
  series.dataFields.value = "value";
  series.dataFields.category = "name";

  var fillModifier = new am4core.LinearGradientModifier();
  fillModifier.brightnesses = [-0.5, 1, -0.5];
  fillModifier.offsets = [0, 0.5, 1];
  series.slices.template.fillModifier = fillModifier;
  series.alignLabels = true;

  series.labels.template.text = "{category}: [bold]{value}[/]";
} // end am4core.ready()

function addBoxes() {
  chartVar = "chartdiv";
  $("#chartdivs").append(`<div id=${chartVar}></div>`);
  trigger(chartVar, 60, 300, 200, 180, 50, 20, 10);

  chartVar += "1";
  $("#chartdivs").append(`<div id=${chartVar}></div>`);
  trigger(chartVar, 560, 200, 10, 180, 50, 20, 10);

  chartVar += "2";
  $("#chartdivs").append(`<div id=${chartVar}></div>`);
  trigger(chartVar, 560, 200, 10, 180, 50, 20, 10);

  chartVar += "4";
  $("#chartdivs").append(`<div id=${chartVar}></div>`);
  trigger(chartVar, 560, 200, 10, 180, 50, 20, 10);
}

addBoxes();
