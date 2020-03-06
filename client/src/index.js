import React from "react";
import ReactDOM from "react-dom";
import "./index.css";
import * as serviceWorker from "./serviceWorker";

import { Route, Link, BrowserRouter as Router, Switch } from "react-router-dom";

import App from "./App";
import MainReport from "./MainReport";
import Upload from "./Upload";
import Users from "./Users";
import TeamReports from "./TeamReports";
import NotFound from "./NotFound";
import TopNavBar from "./TopNavBar";
import RecruiterFilter from "./RecruiterFilter";

const routing = (
  <Router>
    <div>
      <TopNavBar />
      <Switch>
        <Route exact path="/" component={MainReport} />
        <Route path="/upload" component={Upload} />
        <Route path="/users" component={Users} />
        <Route path="/teamReports" component={TeamReports} />
        <Route path="/recruiterFilter" component={RecruiterFilter} />
        <Route component={NotFound} />
      </Switch>
    </div>
  </Router>
);

ReactDOM.render(routing, document.getElementById("root"));

// If you want your app to work offline and load faster, you can change
// unregister() to register() below. Note this comes with some pitfalls.
// Learn more about service workers: https://bit.ly/CRA-PWA
serviceWorker.unregister();
