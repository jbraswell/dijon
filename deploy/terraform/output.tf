output "dijon_instance_info" {
  value = {
    nsg_ids    = oci_core_instance.dijon.create_vnic_details[0].nsg_ids
    public_ip  = oci_core_public_ip.dijon.ip_address
    private_ip = oci_core_instance.dijon.private_ip
  }
}
