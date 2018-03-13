const input_len = 30
const output_len = 5
var pred_in = null;
var pred_out = null;
var model = null

function getRandomInt(max) {
  return Math.floor(Math.random() * Math.floor(max));
}

function initModel()
{
  //load model
  this.model = new KerasJS.Model({
    //this model has an input shape of (1, 30) and an SOFTMAX output of (1, 5)
    filepath: 'model.bin',
    filesystem: true,
    gpu: true
  })
  this.model.ready()
}

function testModel()
{
  //create input with zeros
  this.pred_in = new Float32Array([ .0, .0, .0, .0, .0,
                                    .0, .0, .0, .0, .0,
                                    .0, .0, .0, .0, .0,
                                    .0, .0, .0, .0, .0,
                                    .0, .0, .0, .0, .0,
                                    .0, .0, .0, .0, .0])
  this.pred_out = new Float32Array([.0, .0, .0, .0, .0])
  //load same values to input
  this.pred_in[getRandomInt(30)] = 1
  this.pred_in[getRandomInt(30)] = 1
  this.pred_in[getRandomInt(30)] = 1
  this.pred_in[getRandomInt(30)] = 1
  const inputData = {
    input: this.pred_in
  }
  console.log(inputData);
  console.log(this.pred_out);
  //predict from input
  this.model
  .predict(inputData)
  .then(outputData => {
    this.pred_out = new Float32Array(outputData.output)
    console.log(this.pred_in);
    console.log(this.pred_out);
    $("#out0").text(this.pred_out[0])
    $("#out1").text(this.pred_out[1])
    $("#out2").text(this.pred_out[2])
    $("#out3").text(this.pred_out[3])
    $("#out4").text(this.pred_out[4])
  })
  .catch(err => {
    // handle error
    console.log(err);
  })


}

window.onload = initModel;
