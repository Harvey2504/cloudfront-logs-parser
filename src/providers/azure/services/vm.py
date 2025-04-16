def create_virtual_machines(credential, subscription_id, region):
    """
    Function to manage Azure virtual machines:
    - Establishes connection to Azure
    - Uses existing resource group 'testRG'
    - Checks for existence of testVM1 and testVM2
    - Downgrades VM size to Standard_B1s if necessary
    - Creates Red Hat Enterprise Linux 8.10 x64 Gen2 VMs if they don't exist
    
    Args:
        credential: Azure credentials
        subscription_id: Azure subscription ID
        region: Azure region to create VMs in
    """
    from azure.mgmt.compute import ComputeManagementClient
    from azure.mgmt.network import NetworkManagementClient
    
    # VM configurations
    vm_names = ["testVM1", "testVM2"]
    target_vm_size = "Standard_B1s"
    resource_group_name = "testRG"  # Using your existing resource group
    
    # Initialize clients
    compute_client = ComputeManagementClient(credential, subscription_id)
    network_client = NetworkManagementClient(credential, subscription_id)
    
    print(f"Using existing resource group: {resource_group_name}")
    
    for vm_name in vm_names:
        try:
            # Check if VM exists
            try:
                vm = compute_client.virtual_machines.get(resource_group_name, vm_name)
                print(f"VM {vm_name} exists with size: {vm.hardware_profile.vm_size}")
                
                # Check if VM size needs to be changed
                if vm.hardware_profile.vm_size != target_vm_size:
                    print(f"Changing VM size from {vm.hardware_profile.vm_size} to {target_vm_size}")
                    # Deallocate VM before resizing
                    compute_client.virtual_machines.begin_deallocate(resource_group_name, vm_name).wait()
                    
                    # Update VM size
                    vm.hardware_profile.vm_size = target_vm_size
                    compute_client.virtual_machines.begin_create_or_update(
                        resource_group_name, vm_name, vm
                    ).wait()
                    
                    # Start VM again
                    compute_client.virtual_machines.begin_start(resource_group_name, vm_name).wait()
                    print(f"VM {vm_name} has been resized to {target_vm_size}")
                else:
                    print(f"VM {vm_name} already has the target size {target_vm_size}. Skipping.")
                    
            except Exception as e:
                if "not found" in str(e).lower():
                    print(f"VM {vm_name} not found. Creating it using existing network resources...")
                    
                    # Get references to the existing network resources
                    nic_name = f"{vm_name}-nic"
                    try:
                        nic = network_client.network_interfaces.get(resource_group_name, nic_name)
                        
                        # Create the VM with existing network resources
                        vm_parameters = {
                            "location": region,
                            "hardware_profile": {
                                "vm_size": target_vm_size
                            },
                            "storage_profile": {
                                "image_reference": {
                                    "publisher": "RedHat",
                                    "offer": "RHEL",
                                    "sku": "8_10",  # RHEL 8.10
                                    "version": "latest"
                                },
                                "os_disk": {
                                    "name": f"{vm_name}-osdisk",
                                    "caching": "ReadWrite",
                                    "create_option": "FromImage",
                                    "managed_disk": {
                                        "storage_account_type": "Standard_LRS"
                                    }
                                }
                            },
                            "os_profile": {
                                "computer_name": vm_name,
                                "admin_username": "azureuser",
                                "admin_password": "ComplexPassword@123"  # In production, use key vault or other secure method
                            },
                            "network_profile": {
                                "network_interfaces": [
                                    {
                                        "id": nic.id
                                    }
                                ]
                            },
                            # Set Gen2 configuration
                            "security_profile": {
                                "security_type": "TrustedLaunch",
                                "uefi_settings": {
                                    "secure_boot_enabled": True,
                                    "v_tpm_enabled": True
                                }
                            }
                        }
                        
                        # Create VM
                        compute_client.virtual_machines.begin_create_or_update(
                            resource_group_name, vm_name, vm_parameters
                        ).wait()
                        
                        print(f"VM {vm_name} created with size {target_vm_size} and RHEL 8.10 x64 Gen2")
                    
                    except Exception as nic_error:
                        print(f"Error retrieving or using network interface for {vm_name}: {str(nic_error)}")
                        print("Please make sure the required network resources are created manually before running this function.")
                        
                else:
                    print(f"Error checking VM {vm_name}: {str(e)}")
                    
        except Exception as e:
            print(f"Error processing VM {vm_name}: {str(e)}")