![alt text](<Screenshot 2026-11-02 at 07.09.24.png>) 
![alt text](<Screenshot 2026-11-02 at 07.10.07.png>)
![alt text](<Screenshot 2026-11-02 at 07.09.37.png>) 
![alt text](<Screenshot 2026-11-02 at 07.09.56.png>)


### Infrastructure Reproducibility

To verify reproducibility, I deleted the `capstone-network` CloudFormation stack and recreated it using the same `network.yaml` file.

The deletion completed successfully, and the stack was recreated in **44 seconds** (08:06:36–08:07:20).

No changes to the CloudFormation template were required, and no errors occurred during recreation.

This confirms that the network infrastructure can be recreated using IaC without manually configuring AWS resources.

