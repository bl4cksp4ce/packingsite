import * as THREE from 'node_modules/three';
import { OrbitControls } from 'three/examples/jsm/controls/OrbitControls.js';
//import OrbitControlsLibrary = require('three-orbit-controls');
const OrbitControls = require('three-orbit-controls')(THREE);
var OrbitControls = OrbitControlsLibrary(THREE);
alert("Hello");
//declare var THREE.OrbitControls: any;
console.log("loglog");