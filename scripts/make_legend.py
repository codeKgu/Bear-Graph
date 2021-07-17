import matplotlib.pyplot as plt

NODE_COLORS = ['#453d3c', '#db230b']
LABEL_NAMES = ['Bear Notes', 'Bear Tags']

if __name__ == '__main__':

    def create_legend(colors, label_names):
        f = lambda m,c: plt.plot([],[],marker=m, color=c, ls="none", markersize=11)[0]
        handles = [f("o", colors[i]) for i in range(len(colors))]
        legend = plt.legend(handles, label_names, loc=3, framealpha=1, frameon=False,
                            labelspacing=1)

        def export_legend(legend, filename="legend.png"):
            fig = legend.figure
            fig.canvas.draw()
            bbox = legend.get_window_extent().transformed(fig.dpi_scale_trans.inverted())
            bbox.x1 += 1.6
            bbox.y1 += 0.05
            bbox.y0 -= 0.05
            fig.savefig(filename, dpi=200, bbox_inches=bbox)

        export_legend(legend)

    create_legend(NODE_COLORS, LABEL_NAMES)
