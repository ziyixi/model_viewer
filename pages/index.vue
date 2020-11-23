<template>
  <div>
    <el-container>
      <el-header
        >Model viewer for EARA2020 (East Asia Radially Anisotropic Model
        2020)</el-header
      >
      <el-main>
        <el-row type="flex" class="row-bg" justify="center">
          <el-col :span="15">
            <!-- map -->
            <el-card
              v-loading="loadingmap"
              element-loading-text="It may take several seconds to load depending on your netspeed."
            >
              <div slot="header">
                <span> Map of our simulation region </span>
              </div>
              <el-image
                :src="urlmap"
                fit="fill"
                id="map"
                :preview-src-list="[urlmap]"
              ></el-image>
            </el-card>
            <!-- vertical cross-section  -->
            <el-card
              v-loading="loadingvc"
              element-loading-text="It may take several seconds to load depending on your netspeed."
            >
              <div slot="header">
                <span> Vertical cross-section based on your choice </span>
              </div>
              <el-image
                :src="urlvc"
                fit="fill"
                id="map"
                :preview-src-list="[urlvc]"
              ></el-image>
            </el-card>
          </el-col>
          <el-col :span="9">
            <!-- step bar  -->
            <el-card>
              <el-steps :active="current_step" align-center>
                <el-step
                  title="Step 1"
                  description="Set the great circle line you want to plot the vertical cross-section"
                ></el-step>
                <el-step
                  title="Step 2"
                  description="Configure the vertical cross-section"
                ></el-step>
              </el-steps>
            </el-card>
            <!-- map form  -->
            <el-card>
              <div slot="header">
                <span> Set the line on the map </span>
              </div>
              <el-form ref="formmap" :model="formmap">
                <el-form-item label="Starting point location">
                  <div style="display: flex">
                    <el-input
                      placeholder="Longitude (°)"
                      v-model="formmap.startlon"
                      clearable
                      :disabled="current_step !== 0"
                    >
                    </el-input>
                    <el-input
                      placeholder="Latitude (°)"
                      v-model="formmap.startlat"
                      clearable
                      :disabled="current_step !== 0"
                    >
                    </el-input>
                  </div>
                </el-form-item>
                <el-form-item label="Ending point location ">
                  <div style="display: flex">
                    <el-input
                      placeholder="Longitude (°)"
                      v-model="formmap.endlon"
                      clearable
                      :disabled="current_step !== 0"
                    >
                    </el-input>
                    <el-input
                      placeholder="Latitude (°)"
                      v-model="formmap.endlat"
                      clearable
                      :disabled="current_step !== 0"
                    >
                    </el-input>
                  </div>
                </el-form-item>
                <el-form-item>
                  <el-button
                    type="primary"
                    plain
                    @click="onsubmitmap"
                    :disabled="current_step !== 0"
                    >Submit</el-button
                  >
                  <el-button
                    type="info"
                    plain
                    @click="onclearmap"
                    :disabled="current_step !== 0"
                    >Reset</el-button
                  >
                </el-form-item>
              </el-form>
            </el-card>
            <!-- vc form  -->
            <el-card>
              <div slot="header">
                <span> Configure the vertical-cross-section's plotting </span>
              </div>
              <el-form ref="formvc" :model="formvc">
                <el-form-item label="Parameter">
                  <el-select
                    v-model="formvc.parameter"
                    placeholder="Select parameter"
                    :disabled="current_step !== 1"
                  >
                    <el-option
                      v-for="item in vcoptions.parameter"
                      :key="item.value"
                      :label="item.label"
                      :value="item.value"
                      :disabled="current_step !== 1"
                    >
                    </el-option>
                  </el-select>
                </el-form-item>
                <el-form-item label="X axis label">
                  <el-select
                    v-model="formvc.x_axis_label"
                    placeholder="Select label"
                    :disabled="current_step !== 1"
                  >
                    <el-option
                      v-for="item in vcoptions.x_axis_label"
                      :key="item.value"
                      :label="item.label"
                      :value="item.value"
                    >
                    </el-option>
                  </el-select>
                </el-form-item>
                <el-form-item>
                  <div>
                    <span>Depth of the vertical cross-section (km)</span>
                    <el-slider
                      v-model="formvc.depth"
                      :min="100"
                      :max="1500"
                      show-input
                      :disabled="current_step !== 1"
                    >
                    </el-slider>
                  </div>
                  <div>
                    <span>The colorbar range (%)</span>
                    <el-slider
                      v-model="formvc.colorbar_range"
                      range
                      :max="10"
                      :min="-10"
                      :step="0.5"
                      :disabled="current_step !== 1"
                    >
                    </el-slider>
                  </div>
                </el-form-item>
                <el-form-item>
                  <el-button
                    type="primary"
                    plain
                    @click="onsubmitvc"
                    :disabled="current_step !== 1"
                    >Submit</el-button
                  >
                  <el-button
                    type="info"
                    plain
                    @click="onclearvc"
                    :disabled="current_step !== 1"
                    >Reset</el-button
                  >
                  <el-button
                    type="info"
                    plain
                    @click="onbackvc"
                    :disabled="current_step !== 1"
                    >Back to Step1</el-button
                  >
                </el-form-item>
              </el-form>
            </el-card>
          </el-col>
        </el-row>
      </el-main>
      <el-footer>
        <div class="footer">
          <p style="margin: 0">
            © 2020–2020 Ziyi Xi &nbsp Source codes of the website is available
            at:
            <a href="https://github.com/ziyixi/model_viewer"
              >https://github.com/ziyixi/model_viewer</a
            >
          </p>
        </div>
      </el-footer>
    </el-container>
  </div>
</template>

<script>
export default {
  data() {
    return {
      vcoptions: {
        parameter: [
          { value: "vp", label: "vp" },
          { value: "vs", label: "vs" },
          { value: "vpv", label: "vpv" },
          { value: "vph", label: "vph" },
          { value: "vsv", label: "vsv" },
          { value: "vsh", label: "vsh" },
        ],
        x_axis_label: [
          { label: "Longitude", value: "lon" },
          { label: "Latitude", value: "lat" },
          { label: "Great Circle Distance", value: "dist" },
        ],
      },
      urlmap: require("~/assets/basemap.png"),
      urlvc: require("~/assets/basevc.png"),
      formmap: {
        startlon: null,
        startlat: null,
        endlon: null,
        endlat: null,
      },
      formvc: {
        parameter: null,
        x_axis_label: null,
        depth: 1000,
        colorbar_range: [-3, 3],
      },
      current_step: 0,
      loadingmap: false,
      loadingvc: false,
    };
  },
  methods: {
    onsubmitmap() {
      this.loadingmap = true;
      this.current_step = 1;
      this.requestMap();
    },
    onclearmap() {
      for (var each_key in this.formmap) {
        this.formmap[each_key] = null;
      }
    },
    onsubmitvc() {
      this.loadingvc = true;
      this.requestVc();
    },
    onclearvc() {
      this.formvc = {
        parameter: null,
        x_axis_label: null,
        depth: 1000,
        colorbar_range: [-3, 3],
      };
    },
    onbackvc() {
      this.current_step = 0;
    },
    // user defined functions
    async requestMap() {
      // console.log(this.formmap);
      var response = await this.$axios.post("/map", this.formmap);
      // console.log(response);
      if (response.data === null) {
        this.$message.error(
          "Please place the starting or ending point inside the simulation region (magenta box)"
        );
        this.loadingmap = false;
        this.current_step = 0;
      } else if (response.data === "typeerror") {
        this.$message.error(
          "Please Use the correct type (float) of the coordinates"
        );
        this.loadingmap = false;
        this.current_step = 0;
      } else {
        this.urlmap = this.$config.mapServer + response.data;
        this.loadingmap = false;
      }
    },
    async requestVc() {
      var response = await this.$axios.post("/vc", {
        ...this.formmap,
        ...this.formvc,
      });
      if (response.data === null || response.data === "typeerror") {
        this.$message.error("Please check your form");
        this.loadingvc = false;
      } else {
        this.urlvc = this.$config.vcServer + response.data;
        this.loadingvc = false;
      }
    },
  },
};
</script>

<style>
.el-header,
.el-footer {
  background-color: #ffffff;
  color: #333;
  text-align: center;
  line-height: 60px;
  font-size: 25px;
}

.el-main {
  background-color: #ffffff;
  color: #333;
  text-align: center;
  /* line-height: 560px; */
}
.footer {
  font-size: 15px;
  /* white-space: pre-line; */
}
</style>
