import argparse
import os
import sys
import re
import numpy as np
import pandas as pd


def get_args():
    """Parse commandline."""
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", required=True,
                        help="results csv from checker")
    args = parser.parse_args()
    return args


def main():
    args = get_args()

    df = pd.read_csv(args.input).fillna("")
    df.rename(columns={
        "Organization": "Submitter",
        "Division": "Category",
        "SystemType": "Suite",
        "SystemName": "System",
        "host_processor_model_name": "Processor",
        "host_processor_core_count": "p#",
        "accelerator_model_name": "Accelerator",
        "accelerators_per_node": "a#",
        "notes": "Notes",
    }, inplace=True)
    df.rename(columns={"Model": "UsedModel"}, inplace=True)
    df.rename(columns={"MlperfModel": "Model"}, inplace=True)
    df['a#'] = df['a#'].apply(lambda x: int(x) if x != "" else "")

    df['Unique ID (e.g. for Audit)'] = df.apply(
        lambda x: "/".join([x['Suite'], x['Category'], x['Submitter'], x['Platform']]), axis=1)
    base_url = "https://github.com/mlperf/submissions_inference_0_7/tree/master"
    df['Details'] = df.apply(
        lambda x: '=HYPERLINK("{}","details")'.format("/".join([base_url, x['Category'], x['Submitter'], "results", x['Platform']])), axis=1)

    output = args.input[:-4]
    
    df1 = df[df['Category'] == "closed"].pivot_table(index=[
            'Unique ID (e.g. for Audit)', 'Suite', 'Category', 'Submitter',
            'Availability', 'System', 'Processor', "p#", 'Accelerator', "a#",
            "Details", "Notes",
        ],
        columns=['Model', 'Scenario'],
        values=['Result']
    ).fillna("")
    df1.to_excel(output + "_closed.xlsx")

    df1 = df[df['Category'] == "open"].pivot_table(index=[
            'Unique ID (e.g. for Audit)', 'Suite', 'Category', 'Submitter',
            'Availability', 'System', 'Processor', "p#", 'Accelerator', "a#",
            "Details", "Notes",
        ],
        columns=['Model', 'Scenario'],
        values=['Result']
    ).fillna("")
    df1.to_excel(output + "_open.xlsx")

    return 0


if __name__ == "__main__":
    sys.exit(main())