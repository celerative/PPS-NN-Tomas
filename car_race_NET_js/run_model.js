const input_len = 30
const output_len = 5
var pred_in = null;
var pred_out = null;
var model = null

function initModel()
{
  //load model
  this.model = new KerasJS.Model({
    filepath: 'car_race_model.bin',
    filesystem: true,
    gpu: true
  })
  this.model.ready()
}

// Test model with x_pred and return results in y_pred
// x_pred --> Float32Array(input_len)
// y_pred --> Float32Array(output_len)
function testModel(x_pred, y_pred)
{
  var finnish = false
  if (x_pred === undefined) {
          return;
  }
  if (y_pred === undefined) {
          return;
  }
  //set pred_in to all zeros
  this.pred_in = new Float32Array([ .0, .0, .0, .0, .0,
                                    .0, .0, .0, .0, .0,
                                    .0, .0, .0, .0, .0,
                                    .0, .0, .0, .0, .0,
                                    .0, .0, .0, .0, .0,
                                    .0, .0, .0, .0, .0])
  this.pred_out = new Float32Array([.0, .0, .0, .0, .0])
  //load pred_in with enemies and player
  for (var i = 0; i < this.input_len ; i++) {
    this.pred_in[i] = x_pred[i]
  }
  const inputData = {
    input: this.pred_in
  }
  //predict from input
  this.model
  .predict(inputData)
  .then(outputData => {
    this.pred_out = new Float32Array(outputData.output)
    console.log(this.pred_out);
    for (var i = 0; i < this.output_len ; i++) {
      y_pred[i] = this.pred_out[i]
    }
    finnish = true
  })
  .catch(err => {
    // handle error
    console.log(err);
  })
  // force to wait the promise and results
  while (!finnish) {
  }
  return(y_pred)
}
